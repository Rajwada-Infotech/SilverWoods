from django import template
from django.core.cache import cache
from django.templatetags.static import static
from django.utils.safestring import mark_safe

register = template.Library()

CACHE_KEY = 'page_content'


def _content_map():
    data = cache.get(CACHE_KEY)
    if data is None:
        from core.models import PageContent
        data = {(c.page, c.key): c.value for c in PageContent.objects.all()}
        cache.set(CACHE_KEY, data, 300)
    return data


def clear_content_cache():
    cache.delete(CACHE_KEY)


@register.simple_tag
def cms(page, key, default='', label=''):
    """Editable text block. First render stores the default so it shows up in the admin panel.
    Values may contain simple HTML (e.g. <span class="italic">) — only staff can edit them."""
    data = _content_map()
    if (page, key) not in data:
        from core.models import PageContent
        obj, _ = PageContent.objects.get_or_create(
            page=page, key=key,
            defaults={'value': default, 'label': label or key.replace('_', ' ').title(),
                      'order': PageContent.objects.filter(page=page).count()},
        )
        data[(page, key)] = obj.value
        clear_content_cache()
    return mark_safe(data[(page, key)])


@register.simple_tag
def media_url(obj):
    """URL for a model with an uploaded `image` falling back to a bundled `static_path`."""
    if getattr(obj, 'image', None):
        from core.views import _cloudinary_url
        url = _cloudinary_url(obj.image)
        if url:
            return url
    return static(obj.static_path) if getattr(obj, 'static_path', '') else ''


@register.filter
def fill_area(text, area_range):
    return text.replace('{area_range}', str(area_range))


@register.filter
def digits(value):
    """Keep only digits, e.g. for wa.me links: '+91 98314 05414' -> '919831405414'."""
    return ''.join(ch for ch in str(value or '') if ch.isdigit())
