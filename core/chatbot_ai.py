"""Smart chatbot: FAQ matching + Gemini intent extraction + verified database answers.

The AI is only used to *understand* the question (intent, language, villa type,
budget...). Every fact shown to the visitor comes from the database through the
whitelisted read-only helpers below, so the model can never invent prices or
availability, and it never sees or touches private data (leads, owners, notes).
"""
import json
import logging
import re
import urllib.error
import urllib.request
from decimal import Decimal

from django.core.cache import cache
from django.utils.html import escape

from .models import ChatbotQA, FlatType, ProjectInfo, VillaPlot

log = logging.getLogger(__name__)

MAX_QUESTION_LEN = 300
FAQ_CONFIDENT_SCORE = 2
AI_TIMEOUT_SECONDS = 10
AI_COOLDOWN_SECONDS = 600          # pause AI calls after a quota / rate-limit error
AI_DAILY_CAP = 1000                # stay comfortably inside the free tier

INTENTS = (
    'villa_pricing', 'budget_search', 'area_search', 'plot_availability',
    'plot_status', 'faq', 'contact', 'greeting', 'unknown',
)
LANGS = ('en', 'bn', 'hinglish')
SORTS = ('price_asc', 'price_desc', 'area_desc', 'area_asc')

PLOT_STATUS_LABELS = {
    'en': {'available': 'Available', 'sold': 'Sold', 'reserved': 'Reserved', 'not_for_sale': 'Not for sale'},
    'bn': {'available': 'উপলব্ধ', 'sold': 'বিক্রি হয়ে গেছে', 'reserved': 'সংরক্ষিত', 'not_for_sale': 'বিক্রির জন্য নয়'},
    'hinglish': {'available': 'Available', 'sold': 'Sold ho gaya', 'reserved': 'Reserved', 'not_for_sale': 'Sale ke liye nahi'},
}

# Fixed phrases only; numbers and names are filled in from the database.
TEXT = {
    'en': {
        'sorry': "Sorry, I don't have information about this. Please contact us for further assistance.",
        'best': {'price_asc': 'Most affordable villa:', 'price_desc': 'Most premium villa:', 'area_desc': 'Largest villa:', 'area_asc': 'Most compact villa:'},
        'all_types': 'Here are the current villa types and prices:',
        'one_type': 'Here are the details for {name}:',
        'type_missing': "Sorry, I couldn't find {name} in our current villa list.",
        'budget': 'Villas within your budget of ₹{budget}:',
        'budget_none': 'Sorry, no villa type is currently priced within ₹{budget}. The lowest starting price is ₹{lowest}.',
        'area': 'Villas with built-up area of at least {area} sq.ft:',
        'area_none': 'Sorry, no villa type currently has a built-up area of {area} sq.ft or more. The largest is {largest} sq.ft.',
        'plots': '<strong>{available}</strong> out of <strong>{total}</strong> plots are currently available.',
        'plot_one': 'Plot / Villa #{no}: <strong>{status}</strong>',
        'plot_missing': "Sorry, I couldn't find plot #{no} in our records.",
        'greeting': "Hello! 👋 How can I help you? You can ask about villa prices, sizes, plot availability or the project.",
        'built': 'Built-up', 'terrace': 'Terrace', 'price': 'Price', 'per_sqft': 'per sq.ft',
        'contact_intro': 'You can reach us here:',
    },
    'bn': {
        'sorry': 'দুঃখিত, এই বিষয়ে আমার কাছে তথ্য নেই। আরও সাহায্যের জন্য অনুগ্রহ করে আমাদের সাথে যোগাযোগ করুন।',
        'best': {'price_asc': 'সবচেয়ে কম দামের ভিলা:', 'price_desc': 'সবচেয়ে প্রিমিয়াম ভিলা:', 'area_desc': 'সবচেয়ে বড় ভিলা:', 'area_asc': 'সবচেয়ে ছোট ভিলা:'},
        'all_types': 'বর্তমান ভিলার ধরন ও দাম:',
        'one_type': '{name}-এর বিবরণ:',
        'type_missing': 'দুঃখিত, আমাদের বর্তমান তালিকায় {name} পাওয়া যায়নি।',
        'budget': '₹{budget} বাজেটের মধ্যে ভিলা:',
        'budget_none': 'দুঃখিত, ₹{budget}-এর মধ্যে কোনো ভিলা নেই। সর্বনিম্ন দাম ₹{lowest}।',
        'area': 'কমপক্ষে {area} বর্গফুট বিল্ট-আপ এরিয়ার ভিলা:',
        'area_none': 'দুঃখিত, {area} বর্গফুট বা তার বেশি বিল্ট-আপ এরিয়ার কোনো ভিলা নেই। সবচেয়ে বড়টি {largest} বর্গফুট।',
        'plots': 'মোট <strong>{total}</strong>টি প্লটের মধ্যে <strong>{available}</strong>টি এখন উপলব্ধ।',
        'plot_one': 'প্লট / ভিলা #{no}: <strong>{status}</strong>',
        'plot_missing': 'দুঃখিত, প্লট #{no} আমাদের রেকর্ডে পাওয়া যায়নি।',
        'greeting': 'নমস্কার! 👋 কীভাবে সাহায্য করতে পারি? ভিলার দাম, আকার, প্লটের প্রাপ্যতা বা প্রকল্প সম্পর্কে জিজ্ঞাসা করুন।',
        'built': 'বিল্ট-আপ', 'terrace': 'টেরেস', 'price': 'দাম', 'per_sqft': 'প্রতি বর্গফুট',
        'contact_intro': 'আমাদের সাথে যোগাযোগ করুন:',
    },
    'hinglish': {
        'sorry': "Sorry, iske baare mein mere paas information nahi hai. Please aur help ke liye humse contact karein.",
        'best': {'price_asc': 'Sabse affordable villa:', 'price_desc': 'Sabse premium villa:', 'area_desc': 'Sabse bada villa:', 'area_asc': 'Sabse compact villa:'},
        'all_types': 'Abhi ke villa types aur prices:',
        'one_type': '{name} ki details:',
        'type_missing': 'Sorry, {name} humari current list mein nahi mila.',
        'budget': '₹{budget} budget ke andar villas:',
        'budget_none': 'Sorry, ₹{budget} ke andar koi villa nahi hai. Sabse kam starting price ₹{lowest} hai.',
        'area': 'Kam se kam {area} sq.ft built-up area wale villas:',
        'area_none': 'Sorry, {area} sq.ft ya usse bada koi villa nahi hai. Sabse bada {largest} sq.ft ka hai.',
        'plots': '<strong>{total}</strong> mein se <strong>{available}</strong> plots abhi available hain.',
        'plot_one': 'Plot / Villa #{no}: <strong>{status}</strong>',
        'plot_missing': 'Sorry, plot #{no} humare records mein nahi mila.',
        'greeting': 'Hello! 👋 Main kaise help kar sakta hoon? Villa price, size, plot availability ya project ke baare mein puchiye.',
        'built': 'Built-up', 'terrace': 'Terrace', 'price': 'Price', 'per_sqft': 'per sq.ft',
        'contact_intro': 'Humse yahan contact karein:',
    },
}


# ── Input handling ─────────────────────────────────────────────────────

def clean_question(raw):
    """Trim, collapse whitespace, drop control characters and cap the length."""
    text = ''.join(ch for ch in str(raw or '') if ch.isprintable() or ch == ' ')
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:MAX_QUESTION_LEN]


def detect_lang(text):
    if re.search(r'[ঀ-৿]', text):
        return 'bn'
    return 'en'


# ── Public, read-only data access (the only data the chatbot can reach) ─

def _area_value(text):
    try:
        return float(str(text).replace(',', '').strip())
    except (TypeError, ValueError):
        return None


def public_villa_types():
    """Available villa types with a real price. Never exposes anything but listing fields."""
    rows = []
    for ft in FlatType.objects.filter(is_available=True, price__gt=0).order_by('order', 'name'):
        rows.append({
            'name': ft.name,
            'number': _type_number(ft.name),
            'bhk': ft.bhk,
            'buildup': ft.buildup_area,
            'buildup_value': _area_value(ft.buildup_area),
            'terrace': ft.terrace_area,
            'price': ft.price,
            'price_per_sqft': ft.price_per_sqft,
        })
    return rows


def public_plot_summary():
    total = VillaPlot.objects.count()
    available = VillaPlot.objects.filter(status='available').count()
    return {'total': total, 'available': available}


def public_plot_status(villa_no):
    """Status only. Owner names, reservation holders and notes are private."""
    plot = VillaPlot.objects.filter(villa_no=villa_no).only('villa_no', 'status').first()
    return plot.status if plot else None


def public_contact():
    p = ProjectInfo.load()
    address = ', '.join(x for x in [p.address, p.city if p.city not in p.address else '', p.state] if x)
    if p.pincode:
        address = f'{address} - {p.pincode}'
    return {
        'phone': p.phone, 'whatsapp': getattr(p, 'whatsapp', ''), 'email': p.email, 'address': address,
        'website': p.website, 'facebook': p.facebook, 'instagram': p.instagram,
    }


def _type_number(name):
    m = re.search(r'(\d+)', name or '')
    return int(m.group(1)) if m else None


# ── FAQ (existing keyword system) ──────────────────────────────────────

# Filler words that made unrelated questions match FAQs ("what is the weather in ...")
STOPWORDS = {
    'the', 'and', 'for', 'are', 'was', 'what', 'which', 'who', 'how', 'can', 'you', 'your', 'about',
    'there', 'this', 'that', 'with', 'from', 'have', 'has', 'any', 'today', 'please', 'tell', 'give',
    'kya', 'hai', 'hain', 'kaun', 'kaunsa', 'mujhe', 'aap', 'koi', 'ki', 'ka', 'ke', 'mein',
    'ki', 'ache', 'achhe', 'amar', 'tomader', 'kon', 'kotha', 'ekta', 'ami',
}


def _tokens(q):
    return [w for w in re.findall(r'\w+', q.lower()) if len(w) >= 3 and w not in STOPWORDS]


def faq_scores(q):
    words = _tokens(q)
    scored = []
    for qa in ChatbotQA.objects.filter(is_active=True):
        kws = [kw for kw in qa.keyword_list() if len(kw) >= 3]
        score = sum(1 for w in words if any(w in kw or kw in w for kw in kws))
        if q.lower().strip(' ?') == qa.question.lower().strip(' ?'):
            score += 10
        if score > 0:
            scored.append((score, qa))
    scored.sort(key=lambda x: (-x[0], x[1].order))
    return scored


def render_faq_answer(qa):
    """Existing FAQ answer with live placeholders filled from the database."""
    answer = qa.answer
    if '{{PRICING_TABLE}}' in answer:
        rows = [
            f"• <strong>{escape(ft.name)}</strong> ({ft.bhk} BHK) — "
            f"Buildup: {escape(ft.buildup_area)} | Terrace: {escape(ft.terrace_area)} | "
            f"Price: ₹{ft.price:,.0f} (₹{ft.price_per_sqft:,.0f}/sq.ft)"
            for ft in FlatType.objects.filter(is_available=True).order_by('order')
        ]
        answer = answer.replace('{{PRICING_TABLE}}', '<br>'.join(rows) if rows else 'Contact us for latest pricing.')
    if '{{AVAILABLE_PLOTS}}' in answer:
        s = public_plot_summary()
        answer = answer.replace('{{AVAILABLE_PLOTS}}', f"{s['available']} out of {s['total']}")
    return answer


def faq_follow_up(qa):
    """After the pricing overview, offer the villa-type questions as chips (existing behaviour)."""
    if qa.order != 1:
        return []
    return [{'id': v.id, 'question': v.question}
            for v in ChatbotQA.objects.filter(order__in=range(101, 107), is_active=True).order_by('order')]


# ── Rule-based understanding (works without the AI) ────────────────────

_NUM = r'(\d+(?:\.\d+)?)'
BN_DIGITS = str.maketrans('০১২৩৪৫৬৭৮৯', '0123456789')


def parse_money(text):
    """'1.2 crore' / '120 lakh' / '1,15,00,000' -> rupees (Decimal) or None."""
    t = text.lower().replace(',', '').translate(BN_DIGITS)
    crore = re.search(_NUM + r'\s*(?:crore|cr\b|kotir?\b|koti\b|কোটি)', t)
    lakh = re.search(_NUM + r'\s*(?:lakhs?|lacs?|l\b|লাখ|লক্ষ)', t)
    if crore or lakh:
        total = Decimal(0)
        if crore:
            total += Decimal(crore.group(1)) * Decimal(10_000_000)
        if lakh:
            total += Decimal(lakh.group(1)) * Decimal(100_000)
        return total
    m = re.search(r'(?:₹|rs\.?|inr)\s*(\d{6,})', t)
    if m:
        return Decimal(m.group(1))
    return None


def rule_intent(q):
    t = q.lower().translate(BN_DIGITS)
    m = re.search(r'(?:plot|villa\s*(?:no|number|#)|প্লট)\s*(?:no\.?|number|#)?\s*(\d{1,4})', t)
    if m:
        return {'intent': 'plot_status', 'villa_no': int(m.group(1))}
    m = re.search(r'type\s*-?\s*(\d)\b|(\d)\s*(?:no\.?)?\s*type|টাইপ\s*(\d)', t)
    if m:
        return {'intent': 'villa_pricing', 'villa_type': int(next(g for g in m.groups() if g))}
    money = parse_money(t)
    if money and re.search(r'budget|under|within|below|less|moddhe|moto|ke andar|tak|মধ্যে|বাজেট|ভিতর', t):
        return {'intent': 'budget_search', 'max_price': money}
    if re.search(r'^(hi|hello|hey|namaste|namaskar|নমস্কার|হ্যালো)\b', t):
        return {'intent': 'greeting'}
    return None


# ── Gemini intent extraction ───────────────────────────────────────────

def _ai_key():
    from decouple import config
    return config('GEMINI_API_KEY', default='')


def _ai_model():
    from decouple import config
    # '-latest' alias keeps working as Google retires model versions; lite is fast and has the largest free quota
    return config('GEMINI_MODEL', default='gemini-flash-lite-latest')


def ai_available():
    return bool(_ai_key()) and not cache.get('chatbot_ai_cooldown')


def _bump_daily_ai_count():
    key = 'chatbot_ai_calls_today'
    count = cache.get(key, 0) + 1
    cache.set(key, count, 24 * 3600)
    return count


def ai_extract(q, faqs):
    """Ask Gemini to classify the question. Returns a validated dict or None on any failure."""
    if not ai_available():
        return None
    if _bump_daily_ai_count() > AI_DAILY_CAP:
        cache.set('chatbot_ai_cooldown', True, AI_COOLDOWN_SECONDS)
        return None

    faq_list = '\n'.join(f'{qa.id}: {qa.question}' for qa in faqs)
    prompt = (
        "You classify questions for a real-estate chatbot (Silverwoods villas, Kolkata). "
        "The user may write in English, Bengali (also Bengali typed in English letters, e.g. 'tomader office kothay') "
        "or Hinglish. Use lang=bn for any Bengali, including Bengali in English letters. "
        "Do NOT answer the question; only extract fields.\n"
        "Intents: villa_pricing (price/details of all villa types or one type), budget_search (villas under a budget), "
        "area_search (villas by built-up size), plot_availability (how many plots/villas available), "
        "plot_status (status of one plot or villa number), faq (matches one FAQ below), contact (phone/address/visit), "
        "greeting, unknown (anything else, including requests for personal data about other people).\n"
        "max_price must be in rupees (1 crore = 10000000, 1 lakh = 100000). min_area is in sq.ft.\n"
        "sort: for 'cheapest/lowest price' use price_asc, 'most expensive/premium' price_desc, "
        "'biggest/largest/most spacious' area_desc, 'smallest/compact' area_asc (with intent villa_pricing).\n"
        "Examples: 'সবচেয়ে বড় ভিলা কোনটা?' -> villa_pricing, sort=area_desc, lang=bn. "
        "'sabse sasta ghar kaunsa hai' -> villa_pricing, sort=price_asc, lang=hinglish. "
        "'amar budget 1 kotir moto' -> budget_search, max_price=10000000, lang=bn.\n"
        f"FAQ list (id: question):\n{faq_list}\n\nUser question: {q}"
    )
    schema = {
        'type': 'OBJECT',
        'properties': {
            'intent': {'type': 'STRING', 'enum': list(INTENTS)},
            'lang': {'type': 'STRING', 'enum': list(LANGS)},
            'villa_type': {'type': 'INTEGER', 'nullable': True},
            'villa_no': {'type': 'INTEGER', 'nullable': True},
            'max_price': {'type': 'NUMBER', 'nullable': True},
            'min_area': {'type': 'NUMBER', 'nullable': True},
            'sort': {'type': 'STRING', 'enum': list(SORTS), 'nullable': True},
            'faq_id': {'type': 'INTEGER', 'nullable': True},
        },
        'required': ['intent', 'lang'],
    }
    body = json.dumps({
        'contents': [{'role': 'user', 'parts': [{'text': prompt}]}],
        'generationConfig': {'temperature': 0, 'responseMimeType': 'application/json', 'responseSchema': schema},
    }).encode()
    url = f'https://generativelanguage.googleapis.com/v1beta/models/{_ai_model()}:generateContent'
    req = urllib.request.Request(url, data=body, method='POST', headers={
        'Content-Type': 'application/json', 'x-goog-api-key': _ai_key(),
    })
    try:
        with urllib.request.urlopen(req, timeout=AI_TIMEOUT_SECONDS) as resp:
            payload = json.loads(resp.read().decode())
        text = payload['candidates'][0]['content']['parts'][0]['text']
        return validate_ai_output(json.loads(text), {qa.id for qa in faqs})
    except urllib.error.HTTPError as e:
        if e.code in (429, 403):
            # quota exhausted / rate limited / key disabled: back off and use fallbacks
            cache.set('chatbot_ai_cooldown', True, AI_COOLDOWN_SECONDS)
        log.warning('Chatbot AI HTTP %s', e.code)
    except Exception as e:  # timeout, network, malformed response
        log.warning('Chatbot AI failed: %s', e.__class__.__name__)
    return None


def validate_ai_output(data, faq_ids):
    """Never trust model output: whitelist the intent and range-check every field."""
    if not isinstance(data, dict) or data.get('intent') not in INTENTS:
        return None
    out = {'intent': data['intent'], 'lang': data.get('lang') if data.get('lang') in LANGS else None}

    def as_int(v, lo, hi):
        try:
            v = int(v)
        except (TypeError, ValueError):
            return None
        return v if lo <= v <= hi else None

    def as_dec(v, lo, hi):
        try:
            v = Decimal(str(v))
        except Exception:
            return None
        return v if lo <= v <= hi else None

    out['villa_type'] = as_int(data.get('villa_type'), 1, 50)
    out['villa_no'] = as_int(data.get('villa_no'), 1, 9999)
    out['max_price'] = as_dec(data.get('max_price'), 100_000, 10_000_000_000)
    out['min_area'] = as_dec(data.get('min_area'), 100, 100_000)
    faq_id = as_int(data.get('faq_id'), 1, 10**9)
    out['faq_id'] = faq_id if faq_id in faq_ids else None
    out['sort'] = data.get('sort') if data.get('sort') in SORTS else None
    if out['intent'] == 'faq' and not out['faq_id']:
        out['intent'] = 'unknown'
    return out


# ── Answer building from verified data ─────────────────────────────────

def _money(v):
    return f'{Decimal(v):,.0f}'


def _type_line(t, L):
    parts = [f"• <strong>{escape(t['name'])}</strong> ({t['bhk']} BHK)"]
    details = []
    if t['buildup']:
        details.append(f"{L['built']}: {escape(t['buildup'])} sq.ft")
    if t['terrace']:
        details.append(f"{L['terrace']}: {escape(t['terrace'])} sq.ft")
    details.append(f"{L['price']}: ₹{_money(t['price'])}")
    if t['price_per_sqft']:
        details.append(f"₹{_money(t['price_per_sqft'])} {L['per_sqft']}")
    return parts[0] + ' — ' + ' | '.join(details)


def build_answer(info, lang):
    """Return (html, found). found=False means show the polite 'no information' reply."""
    L = TEXT[lang]
    intent = info.get('intent')
    if intent == 'greeting':
        return L['greeting'], True

    if intent == 'villa_pricing':
        types = public_villa_types()
        if not types:
            return L['sorry'], False
        wanted = info.get('villa_type')
        if wanted:
            match = [t for t in types if t['number'] == wanted]
            if not match:
                return L['type_missing'].format(name=f'Villa Type {wanted}'), False
            return L['one_type'].format(name=escape(match[0]['name'])) + '<br>' + _type_line(match[0], L), True
        sort = info.get('sort')
        if sort:
            key = (lambda t: t['price']) if sort.startswith('price') else (lambda t: t['buildup_value'] or 0)
            ranked = sorted(types, key=key, reverse=sort.endswith('desc'))
            return L['best'][sort] + '<br>' + _type_line(ranked[0], L), True
        return L['all_types'] + '<br>' + '<br>'.join(_type_line(t, L) for t in types), True

    if intent == 'budget_search' and info.get('max_price'):
        types = public_villa_types()
        if not types:
            return L['sorry'], False
        budget = info['max_price']
        within = [t for t in types if t['price'] <= budget]
        if not within:
            lowest = min(t['price'] for t in types)
            return L['budget_none'].format(budget=_money(budget), lowest=_money(lowest)), True
        within.sort(key=lambda t: t['price'])
        return L['budget'].format(budget=_money(budget)) + '<br>' + '<br>'.join(_type_line(t, L) for t in within), True

    if intent == 'area_search' and info.get('min_area'):
        types = [t for t in public_villa_types() if t['buildup_value']]
        if not types:
            return L['sorry'], False
        area = float(info['min_area'])
        big = sorted([t for t in types if t['buildup_value'] >= area], key=lambda t: t['buildup_value'])
        if not big:
            largest = max(t['buildup_value'] for t in types)
            return L['area_none'].format(area=f'{area:,.0f}', largest=f'{largest:,.2f}'), True
        return L['area'].format(area=f'{area:,.0f}') + '<br>' + '<br>'.join(_type_line(t, L) for t in big), True

    if intent == 'plot_availability':
        s = public_plot_summary()
        if not s['total']:
            return L['sorry'], False
        return L['plots'].format(**s), True

    if intent == 'plot_status' and info.get('villa_no'):
        status = public_plot_status(info['villa_no'])
        if not status:
            return L['plot_missing'].format(no=info['villa_no']), False
        label = PLOT_STATUS_LABELS[lang].get(status, status)
        return L['plot_one'].format(no=info['villa_no'], status=escape(label)), True

    return L['sorry'], False


# ── Rate limiting ──────────────────────────────────────────────────────

def client_ip(request):
    fwd = request.META.get('HTTP_X_FORWARDED_FOR', '')
    ip = fwd.split(',')[0].strip() if fwd else request.META.get('REMOTE_ADDR', '')
    return ip[:64] or 'unknown'


def rate_limited(request, per_minute=15, per_day=300):
    ip = client_ip(request)
    for window, limit, ttl in (('m', per_minute, 60), ('d', per_day, 24 * 3600)):
        key = f'chatbot_rl_{window}_{ip}'
        cache.add(key, 0, ttl)          # starts the window; no-op if it already exists
        try:
            count = cache.incr(key)
        except ValueError:              # expired between add and incr
            cache.set(key, 1, ttl)
            count = 1
        if count > limit:
            return True
    return False


# ── Main entry point ───────────────────────────────────────────────────

def answer_question(raw_question):
    """Returns a JSON-safe dict for the chatbot UI."""
    q = clean_question(raw_question)
    lang = detect_lang(q)
    if len(q) < 2:
        return {'answer': TEXT[lang]['sorry'], 'source': 'invalid', 'show_contact': True}

    # 1. Specific details (plot number, villa type, budget) go straight to the live data
    info = rule_intent(q)
    source = 'rules'

    # 2. Existing FAQ keywords (fast, free, admin-curated)
    scored = faq_scores(q)
    if info is None and scored and scored[0][0] >= FAQ_CONFIDENT_SCORE:
        qa = scored[0][1]
        return {'answer': render_faq_answer(qa), 'source': 'faq', 'faq_id': qa.id, 'follow_up': faq_follow_up(qa)}

    # 3. Gemini for everything else (multilingual understanding only)
    if info is None:
        faqs = list(ChatbotQA.objects.filter(is_active=True).only('id', 'question'))
        info = ai_extract(q, faqs)
        source = 'ai'
        if info and info.get('lang'):
            lang = info['lang']

    if info:
        if info['intent'] == 'faq':
            qa = ChatbotQA.objects.filter(pk=info['faq_id'], is_active=True).first()
            if qa:
                return {'answer': render_faq_answer(qa), 'source': 'ai_faq', 'faq_id': qa.id, 'follow_up': faq_follow_up(qa)}
        if info['intent'] == 'contact':
            return {'answer': TEXT[lang]['contact_intro'], 'source': source, 'show_contact': True}
        html, found = build_answer(info, lang)
        return {'answer': html, 'source': source, 'show_contact': not found}

    # 4. AI unavailable or unsure: fall back to the best keyword match, then a polite reply
    if scored:
        qa = scored[0][1]
        return {'answer': render_faq_answer(qa), 'source': 'faq_fallback', 'faq_id': qa.id, 'follow_up': faq_follow_up(qa)}
    return {'answer': TEXT[lang]['sorry'], 'source': 'fallback', 'show_contact': True,
            'suggest': [{'id': qa.id, 'question': qa.question} for qa in ChatbotQA.objects.filter(is_active=True)[:6]]}
