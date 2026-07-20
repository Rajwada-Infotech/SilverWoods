import csv
import io
import json
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string
from django.utils import timezone
from django.db import models
from django.db.models import Max
from .models import (
    ProjectInfo, FlatType, Amenity, Lead, SiteVisitor,
    PopupAd, Review, BuildingFlat, BrochureImage, VillaPlot, ChatbotQA
)
from .forms import LeadForm, PopupAdForm, FlatTypeForm, ReviewForm
import os as _os
from decouple import config as _decouple_config

def _cloudinary_active():
    """True if Cloudinary credentials are available (for URL building) — checks os.environ + .env."""
    return bool(_os.environ.get('CLOUDINARY_URL') or _decouple_config('CLOUDINARY_URL', default=None))

def _direct_upload_active():
    """True only when CLOUDINARY_URL is set via os.environ (Railway production), not just .env.
    Keeps direct upload JS off on localhost so regular form upload is used instead."""
    return bool(_os.environ.get('CLOUDINARY_URL'))


def _cloudinary_url(file_field):
    """Build the correct URL: Cloudinary in production, local /media/ on localhost."""
    if not file_field:
        return ''
    name = file_field.name if hasattr(file_field, 'name') else str(file_field)
    if not name:
        return ''
    try:
        if _direct_upload_active():
            import cloudinary
            cloud_name = cloudinary.config().cloud_name
            ext = name.lower().rsplit('.', 1)[-1] if '.' in name else ''
            resource_type = 'video' if ext in ('mp4', 'webm', 'mov', 'avi') else 'image'
            # f_auto → best format per browser (WebP/WebM for modern, JPG/MP4 for old)
            # q_auto → Cloudinary picks optimal quality automatically
            transform = 'f_auto,q_auto'
            return f'https://res.cloudinary.com/{cloud_name}/{resource_type}/upload/{transform}/{name}'
        return file_field.url
    except Exception:
        return ''


def track_visitor(request):
    pass


def index(request):
    track_visitor(request)
    from django.core.cache import cache

    project = cache.get('index_project')
    if project is None:
        project = ProjectInfo.load()
        cache.set('index_project', project, 300)

    flat_types = cache.get('index_flat_types')
    area_range = cache.get('index_area_range')
    if flat_types is None or area_range is None:
        flat_types = list(FlatType.objects.filter(is_available=True))
        def _parse_area(s):
            try: return float(s.replace(',', ''))
            except: return None
        villa_fts = FlatType.objects.filter(name__icontains='villa type')
        buildup_vals = [v for v in (_parse_area(ft.buildup_area) for ft in villa_fts) if v]
        area_range = f"{min(buildup_vals):,.2f} to {max(buildup_vals):,.2f} sq. ft." if buildup_vals else "—"
        cache.set('index_flat_types', flat_types, 300)
        cache.set('index_area_range', area_range, 300)

    amenities = cache.get('index_amenities')
    if amenities is None:
        amenities = list(Amenity.objects.all())
        cache.set('index_amenities', amenities, 300)

    reviews = cache.get('index_reviews')
    if reviews is None:
        reviews = list(Review.objects.filter(is_approved=True, rating=5).order_by('-created_at')[:3])
        cache.set('index_reviews', reviews, 300)

    popups = cache.get('index_popups')
    if popups is None:
        popups = list(PopupAd.objects.filter(is_active=True))
        cache.set('index_popups', popups, 300)
    lead_form = LeadForm()
    review_form = ReviewForm()

    if request.method == 'POST':
        if 'lead_submit' in request.POST:
            lead_form = LeadForm(request.POST)
            if lead_form.is_valid():
                lead_form.save()
                return JsonResponse({'success': True, 'message': 'Thank you! We will contact you soon.'})
            return JsonResponse({'success': False, 'errors': lead_form.errors})
        elif 'review_submit' in request.POST:
            review_form = ReviewForm(request.POST)
            if review_form.is_valid():
                review = review_form.save(commit=False)
                review.is_approved = True
                review.save()
                return JsonResponse({'success': True, 'message': 'Thank you for your review!'})
            return JsonResponse({'success': False, 'errors': review_form.errors})

    return render(request, 'index.html', {
        'project': project,
        'flat_types': flat_types,
        'area_range': area_range,
        'amenities': amenities,
        'reviews': reviews,
        'popups': popups,
        'lead_form': lead_form,
        'review_form': review_form,
    })


def submit_lead(request):
    if request.method == 'POST':
        form = LeadForm(request.POST)
        if form.is_valid():
            lead = form.save(commit=False)
            source = request.POST.get('source', 'website')
            if source:
                lead.source = source
            popup_ad_id = request.POST.get('popup_ad_id')
            if popup_ad_id:
                try:
                    lead.popup_ad = PopupAd.objects.get(pk=popup_ad_id)
                except PopupAd.DoesNotExist:
                    pass
            lead.save()
            return JsonResponse({'success': True, 'message': 'Thank you! We will contact you soon.'})
        return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'success': False, 'message': 'Invalid request'})


def visitor_count(request):
    count = SiteVisitor.objects.count()
    return JsonResponse({'count': count})


def track_visit(request):
    if request.method == 'POST':
        x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
        ip = x_forwarded.split(',')[0] if x_forwarded else request.META.get('REMOTE_ADDR')
        SiteVisitor.objects.create(
            ip_address=ip,
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
            page_visited='/',
        )
    count = SiteVisitor.objects.count()
    return JsonResponse({'count': count})


def all_reviews(request):
    """Return all approved reviews with rating 3-5, optionally filtered by rating."""
    rating = request.GET.get('rating')
    qs = Review.objects.filter(is_approved=True, rating__gte=3).order_by('-created_at')
    if rating:
        qs = qs.filter(rating=int(rating))
    data = [
        {
            'name': r.name,
            'rating': r.rating,
            'comment': r.comment,
            'designation': r.designation,
            'date': r.created_at.strftime('%b %Y'),
        }
        for r in qs
    ]
    return JsonResponse({'reviews': data})


def submit_review(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.is_approved = True
            review.save()
            return JsonResponse({'success': True, 'message': 'Thank you for your review!'})
        return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'success': False, 'message': 'Invalid request'})


def download_brochure(request):
    from django.http import HttpResponseRedirect
    from django.templatetags.static import static
    return HttpResponseRedirect(static('brochure/silverwoods_brochure.pdf'))


def brochure(request):
    from django.templatetags.static import static
    # Brochure pages are 1.webp to 25.webp in static/brochure/
    image_urls = [static(f'brochure/{i}.webp') for i in range(1, 26)]
    return render(request, 'brochure.html', {'image_urls': image_urls})


def blueprint(request):
    flats = BuildingFlat.objects.select_related('flat_type').all()
    flat_data = []
    for f in flats:
        flat_data.append({
            'id': f.id,
            'tower': f.tower,
            'floor': f.floor,
            'flat_number': f.flat_number,
            'type': f'{f.flat_type.bhk} BHK',
            'area': f.flat_type.carpet_area,
            'price': str(f.flat_type.price),
            'status': f.status,
        })
    def fmt_price(p):
        p = int(p)
        if p >= 10000000:
            return f'₹{p/10000000:.2f} Cr'
        elif p >= 100000:
            return f'₹{p/100000:.2f} L'
        return f'₹{p:,}'

    villa_prices = {}
    villa_areas = {}
    for ft in FlatType.objects.filter(name__icontains='villa type'):
        import re
        m = re.search(r'(\d+)', ft.name)
        if m:
            t = int(m.group(1))
            if ft.price:
                villa_prices[t] = fmt_price(ft.price)
            villa_areas[t] = {
                'buildup': ft.buildup_area or '—',
                'terrace': ft.terrace_area or '—',
                'total': ft.super_buildup_area or '—',
            }

    return render(request, 'blueprint.html', {
        'flats': json.dumps(flat_data),
        'villa_prices_json': json.dumps(villa_prices),
        'villa_areas_json': json.dumps(villa_areas),
    })


def walkthrough(request):
    return render(request, 'walkthrough.html')


def plots(request):
    # Brochure plots 1-121 excluding 30,31 (Marketing Office) = 119 plots
    all_plot_nos = [i for i in range(1, 122) if i not in (30, 31)]
    existing = set(VillaPlot.objects.values_list('villa_no', flat=True))
    missing = [i for i in all_plot_nos if i not in existing]
    if missing:
        VillaPlot.objects.bulk_create([VillaPlot(villa_no=i) for i in missing], ignore_conflicts=True)
    # Auto-expire reservations whose time has passed
    VillaPlot.objects.filter(status='reserved', reserved_until__lt=timezone.now()).update(
        status='available', reserved_by='', reserved_until=None)
    plot_qs = VillaPlot.objects.filter(villa_no__in=all_plot_nos)
    plots_data = {
        p.villa_no: {
            'status': p.status,
            'owner': p.owner_name,
            'completion_pct': p.completion_pct,
            'reserved_until': p.reserved_until.isoformat() if p.reserved_until else None,
        }
        for p in plot_qs
    }
    sold = sum(1 for p in plots_data.values() if p['status'] == 'sold')
    reserved = sum(1 for p in plots_data.values() if p['status'] == 'reserved')
    nfs = sum(1 for p in plots_data.values() if p['status'] == 'not_for_sale')

    import re as _re
    def fmt_price(p):
        p = int(p)
        if p >= 10000000: return f'₹{p/10000000:.2f} Cr'
        elif p >= 100000: return f'₹{p/100000:.2f} L'
        return f'₹{p:,}'
    villa_prices = {}
    villa_areas = {}
    for ft in FlatType.objects.filter(name__icontains='villa type'):
        m = _re.search(r'(\d+)', ft.name)
        if m:
            t = int(m.group(1))
            if ft.price:
                villa_prices[t] = fmt_price(ft.price)
            villa_areas[t] = {
                'buildup': ft.buildup_area or '—',
                'terrace': ft.terrace_area or '—',
                'total': ft.super_buildup_area or '—',
            }

    return render(request, 'plots.html', {
        'plots_json': json.dumps(plots_data),
        'villa_prices_json': json.dumps(villa_prices),
        'villa_areas_json': json.dumps(villa_areas),
        'sold': sold,
        'reserved': reserved,
        'nfs': nfs,
        'available': 119 - sold - reserved - nfs,
    })


def api_plots(request):
    plot_qs = VillaPlot.objects.all()
    data = {p.villa_no: {'status': p.status, 'owner': p.owner_name, 'completion_pct': p.completion_pct} for p in plot_qs}
    return JsonResponse(data)


def get_popups(request):
    from django.db.models import Q
    from django.core.cache import cache
    today = timezone.localdate()
    expired = PopupAd.objects.filter(is_active=True, end_date__lt=today)
    if expired.exists():
        max_order = PopupAd.objects.aggregate(m=Max('order'))['m'] or 0
        for i, ad in enumerate(expired, start=1):
            ad.is_active = False
            ad.order = max_order + i
            ad.save(update_fields=['is_active', 'order'])
        cache.delete('api_popups')

    cached = cache.get('api_popups')
    if cached is not None:
        return JsonResponse({'popups': cached})

    popups = PopupAd.objects.filter(is_active=True).filter(
        Q(start_date__isnull=True) | Q(start_date__lte=today)
    ).filter(
        Q(end_date__isnull=True) | Q(end_date__gte=today)
    ).order_by('order', '-created_at')
    data = []
    for p in popups:
        img_name = p.image.name.lower() if p.image else ''
        is_video = any(img_name.endswith(ext) for ext in ['.mp4', '.webm', '.mov'])
        data.append({
            'id': p.id,
            'title': p.title,
            'description': p.description,
            'image': _cloudinary_url(p.image),
            'is_video': is_video,
            'flat_type': p.flat_type,
            'link': p.link,
            'is_external': p.is_external,
            'project_logo': _cloudinary_url(p.project_logo),
        })
    cache.set('api_popups', data, 120)
    return JsonResponse({'popups': data})


# ─── Admin Panel Views ───

def admin_login(request):
    if request.user.is_authenticated:
        return redirect('admin_dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user and user.is_staff:
            login(request, user)
            return redirect('admin_dashboard')
        return render(request, 'admin_panel/login.html', {'error': 'Invalid credentials'})
    return render(request, 'admin_panel/login.html')


def admin_logout(request):
    logout(request)
    return redirect('home')


@login_required
def admin_dashboard(request):
    all_plot_nos = [i for i in range(1, 122) if i not in (30, 31)]
    total_leads = Lead.objects.count()
    new_leads = Lead.objects.filter(is_contacted=False).count()
    total_visitors = SiteVisitor.objects.count()
    plot_qs = VillaPlot.objects.filter(villa_no__in=all_plot_nos)
    total_plots = 119
    sold_plots = plot_qs.filter(status='sold').count()
    reserved_plots = plot_qs.filter(status='reserved').count()
    nfs_plots = plot_qs.filter(status='not_for_sale').count()
    available_plots = total_plots - sold_plots - reserved_plots - nfs_plots
    active_popups = PopupAd.objects.filter(is_active=True).count()
    recent_leads = Lead.objects.all()[:10]

    return render(request, 'admin_panel/dashboard.html', {
        'total_leads': total_leads,
        'new_leads': new_leads,
        'total_visitors': total_visitors,
        'total_plots': total_plots,
        'sold_plots': sold_plots,
        'reserved_plots': reserved_plots,
        'nfs_plots': nfs_plots,
        'available_plots': available_plots,
        'active_popups': active_popups,
        'recent_leads': recent_leads,
    })


@login_required
def admin_leads(request):
    leads = Lead.objects.all()
    source_filter = request.GET.getlist('source')
    project_filter = request.GET.getlist('project')
    date_from = request.GET.get('date_from') or None
    date_to = request.GET.get('date_to') or None
    if date_from == 'None': date_from = None
    if date_to == 'None': date_to = None
    if source_filter:
        leads = leads.filter(source__in=source_filter)
    if project_filter:
        leads = leads.filter(popup_ad__title__in=project_filter)
    if date_from:
        leads = leads.filter(created_at__date__gte=date_from)
    if date_to:
        leads = leads.filter(created_at__date__lte=date_to)
    all_sources = Lead.objects.order_by('source').values_list('source', flat=True).distinct()
    all_projects = PopupAd.objects.values_list('title', flat=True).distinct()
    return render(request, 'admin_panel/leads.html', {
        'leads': leads,
        'all_sources': all_sources,
        'all_projects': all_projects,
        'selected_sources': source_filter,
        'selected_projects': project_filter,
        'date_from': date_from,
        'date_to': date_to,
    })


@login_required
def export_leads(request, format):
    leads = Lead.objects.all()
    source_filter = request.GET.getlist('source')
    project_filter = request.GET.getlist('project')
    date_from = request.GET.get('date_from') or None
    date_to = request.GET.get('date_to') or None
    if date_from == 'None': date_from = None
    if date_to == 'None': date_to = None
    if source_filter:
        leads = leads.filter(source__in=source_filter)
    if project_filter:
        leads = leads.filter(popup_ad__title__in=project_filter)
    if date_from:
        leads = leads.filter(created_at__date__gte=date_from)
    if date_to:
        leads = leads.filter(created_at__date__lte=date_to)

    today = timezone.localdate().strftime('%Y-%m-%d')
    if project_filter:
        proj_slug = '_'.join(p.replace(' ', '_') for p in project_filter)
        base_filename = f"{proj_slug}_{today}"
    else:
        base_filename = f"leads_{today}"

    if format == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{base_filename}.csv"'
        writer = csv.writer(response)
        writer.writerow(['Name', 'Email', 'Phone', 'Flat Preference', 'Message', 'Source', 'Project', 'Date', 'Contacted'])
        for lead in leads:
            writer.writerow([lead.name, lead.email, lead.phone, lead.flat_preference,
                             lead.message, lead.get_source_display_label(),
                             lead.popup_ad.title if lead.popup_ad else '—',
                             lead.created_at.strftime('%Y-%m-%d %H:%M'), 'Yes' if lead.is_contacted else 'No'])
        return response

    elif format == 'excel':
        try:
            import openpyxl
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Leads"
            headers = ['Name', 'Email', 'Phone', 'Flat Preference', 'Message', 'Source', 'Project', 'Date', 'Contacted']
            ws.append(headers)
            for lead in leads:
                ws.append([lead.name, lead.email, lead.phone, lead.flat_preference,
                           lead.message, lead.get_source_display_label(),
                           lead.popup_ad.title if lead.popup_ad else '—',
                           lead.created_at.strftime('%Y-%m-%d %H:%M'),
                           'Yes' if lead.is_contacted else 'No'])
            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename="{base_filename}.xlsx"'
            wb.save(response)
            return response
        except ImportError:
            return HttpResponse("openpyxl not installed", status=500)

    elif format == 'pdf':
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4, landscape
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=landscape(A4))
            data = [['Name', 'Email', 'Phone', 'Flat Pref', 'Message', 'Source', 'Project', 'Date', 'Contacted']]
            for lead in leads:
                data.append([
                    lead.name, lead.email, lead.phone,
                    lead.flat_preference or '—',
                    (lead.message or '—')[:40],
                    lead.get_source_display_label(),
                    lead.popup_ad.title if lead.popup_ad else '—',
                    lead.created_at.strftime('%Y-%m-%d'),
                    'Yes' if lead.is_contacted else 'No',
                ])
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
            ]))
            doc.build([table])
            buffer.seek(0)
            response = HttpResponse(buffer, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{base_filename}.pdf"'
            return response
        except ImportError:
            return HttpResponse("reportlab not installed", status=500)

    return HttpResponse("Invalid format", status=400)


@login_required
def admin_pricing(request):
    flat_types = FlatType.objects.all()
    if request.method == 'POST':
        flat_id = request.POST.get('flat_id')
        if flat_id:
            flat = get_object_or_404(FlatType, pk=flat_id)
            form = FlatTypeForm(request.POST, instance=flat)
        else:
            form = FlatTypeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_pricing')
    return render(request, 'admin_panel/pricing.html', {'flat_types': flat_types, 'form': FlatTypeForm()})


@login_required
def admin_delete_flat_type(request, pk):
    flat = get_object_or_404(FlatType, pk=pk)
    flat.delete()
    return redirect('admin_pricing')


@login_required
def admin_popups(request):
    import traceback as _tb
    try:
        return _admin_popups_inner(request)
    except Exception as _e:
        import logging
        logging.getLogger(__name__).error('admin_popups 500: %s\n%s', _e, _tb.format_exc())
        raise


@login_required
def cloudinary_sign_upload(request):
    """Return signed params for a direct browser-to-Cloudinary upload."""
    import os, time
    if not _cloudinary_active():
        return JsonResponse({'error': 'Cloudinary not configured'}, status=400)
    import cloudinary, cloudinary.utils
    folder = request.GET.get('folder', 'popups')
    public_id = request.GET.get('public_id', '').strip()
    timestamp = int(time.time())
    params = {'timestamp': timestamp}
    if public_id:
        params['public_id'] = public_id
        params['overwrite'] = True
        params['invalidate'] = True
    else:
        params['folder'] = folder
    signature = cloudinary.utils.api_sign_request(params, cloudinary.config().api_secret)
    resp = {
        'cloud_name': cloudinary.config().cloud_name,
        'api_key': cloudinary.config().api_key,
        'timestamp': timestamp,
        'signature': signature,
        'folder': folder,
    }
    if public_id:
        resp['public_id'] = public_id
    return JsonResponse(resp)


def _admin_popups_inner(request):
    import os as _os
    cloudinary_active = _direct_upload_active()
    popups = PopupAd.objects.all()
    popup_error = ''
    if request.method == 'POST':
        popup_id = request.POST.get('popup_id')
        # Reject files over 100 MB only when direct upload is NOT active (file goes through Django)
        if not cloudinary_active:
            for f in request.FILES.values():
                if f.size > 100 * 1024 * 1024:
                    popup_error = f'"{f.name}" is too large ({f.size // (1024*1024)} MB). Maximum file size is 100 MB.'
                    _enriched = []
                    for p in popups:
                        p.logo_url_cdn = _cloudinary_url(p.project_logo)
                        p.image_url_cdn = _cloudinary_url(p.image)
                        _enriched.append(p)
                    return render(request, 'admin_panel/popups.html', {
                        'popups': _enriched, 'form': PopupAdForm(), 'popup_error': popup_error,
                    })
        # Check for direct-upload public_ids (browser uploaded straight to Cloudinary)
        image_public_id = request.POST.get('image_public_id', '').strip()
        logo_public_id = request.POST.get('logo_public_id', '').strip()
        print(f'[popup_save] POST image_public_id={image_public_id!r} logo_public_id={logo_public_id!r}')

        # Remove files from FILES if we have a direct-upload public_id (avoid double upload)
        files = request.FILES.copy()
        if image_public_id:
            files.pop('image', None)
        if logo_public_id:
            files.pop('project_logo', None)

        if popup_id:
            popup = get_object_or_404(PopupAd, pk=popup_id)
            old_image = popup.image.name if popup.image else None
            old_logo = popup.project_logo.name if popup.project_logo else None
            form = PopupAdForm(request.POST, files, instance=popup)
        else:
            old_image = old_logo = None
            form = PopupAdForm(request.POST, files)
        if form.is_valid():
            if not popup_id:
                PopupAd.objects.all().update(order=models.F('order') + 1)
                instance = form.save(commit=False)
                instance.order = 0
            else:
                instance = form.save(commit=False)
                was_active = PopupAd.objects.filter(pk=popup_id).values_list('is_active', flat=True).first()
                if was_active and not instance.is_active:
                    max_order = PopupAd.objects.aggregate(m=Max('order'))['m'] or 0
                    instance.order = max_order + 1
            # Apply direct-upload paths — move from temp folder to permanent on save
            if image_public_id:
                if old_image and old_image != image_public_id:
                    _cloudinary_delete(type('F', (), {'name': old_image})())
                image_public_id = _cloudinary_promote_temp(image_public_id)
                instance.image = image_public_id
            if logo_public_id:
                if old_logo and old_logo != logo_public_id:
                    _cloudinary_delete(type('F', (), {'name': old_logo})())
                logo_public_id = _cloudinary_promote_temp(logo_public_id)
                instance.project_logo = logo_public_id
            instance.save()
            from django.core.cache import cache
            cache.delete('api_popups')
            cache.delete('index_popups')
            return redirect('admin_popups')
    enriched = []
    for p in popups:
        p.logo_url_cdn = _cloudinary_url(p.project_logo)
        p.image_url_cdn = _cloudinary_url(p.image)
        enriched.append(p)
    return render(request, 'admin_panel/popups.html', {
        'popups': enriched, 'form': PopupAdForm(),
        'popup_error': popup_error, 'cloudinary_active': cloudinary_active,
    })


@login_required
def admin_reorder_popups(request):
    if request.method == 'POST':
        import json
        ids = json.loads(request.body).get('ids', [])
        for index, pk in enumerate(ids, start=1):
            PopupAd.objects.filter(pk=pk).update(order=index)
        return JsonResponse({'ok': True})
    return JsonResponse({'ok': False}, status=400)


@login_required
def admin_toggle_popup(request, pk):
    popup = get_object_or_404(PopupAd, pk=pk)
    popup.is_active = not popup.is_active
    if not popup.is_active:
        max_order = PopupAd.objects.aggregate(m=Max('order'))['m'] or 0
        popup.order = max_order + 1
    popup.save()
    from django.core.cache import cache
    cache.delete('api_popups')
    cache.delete('index_popups')
    return redirect('admin_popups')


def _cloudinary_promote_temp(stored_name):
    """Move a temp-folder asset to its permanent location on Save.

    stored_name is like 'popups/temp/abc.jpg' or 'popups/temp/logos/abc.jpg'.
    Returns the permanent stored_name, or the original if it's not in temp.
    """
    if not _cloudinary_active() or not stored_name:
        print(f'[promote_temp] skipped — active={_cloudinary_active()} stored_name={stored_name!r}')
        return stored_name
    if '/temp/' not in stored_name:
        print(f'[promote_temp] no /temp/ in {stored_name!r}, skipping')
        return stored_name  # already permanent, nothing to do
    try:
        import cloudinary.uploader
        ext = stored_name.rsplit('.', 1)[-1].lower() if '.' in stored_name else ''
        from_public_id = stored_name.rsplit('.', 1)[0]  # strip extension
        to_public_id = from_public_id.replace('/temp/', '/', 1)
        resource_type = 'video' if ext in ('mp4', 'webm', 'mov', 'avi') else 'image'
        print(f'[promote_temp] renaming {from_public_id!r} → {to_public_id!r} ({resource_type})')
        cloudinary.uploader.rename(
            from_public_id, to_public_id,
            resource_type=resource_type,
            overwrite=True, invalidate=True,
        )
        print(f'[promote_temp] rename OK, destroying temp {from_public_id!r}')
        try:
            dr = cloudinary.uploader.destroy(from_public_id, resource_type=resource_type, invalidate=True)
            print(f'[promote_temp] destroy result: {dr}')
            # If destroy says "not found", rename didn't actually move it — try deleting by to_public_id
            if dr.get('result') == 'not found':
                print(f'[promote_temp] temp still exists, trying destroy on renamed id {to_public_id!r}')
                # File might still be in temp under original id but rename returned wrong result
                # Try force-deleting via admin API
                import cloudinary.api
                try:
                    cloudinary.api.delete_resources([from_public_id], resource_type=resource_type, invalidate=True)
                    print(f'[promote_temp] admin delete done')
                except Exception as e2:
                    print(f'[promote_temp] admin delete failed: {e2}')
        except Exception as e:
            print(f'[promote_temp] destroy failed: {e}')
        return to_public_id + '.' + ext if ext else to_public_id
    except Exception as e:
        print(f'[promote_temp] ERROR: {e}')
        return stored_name  # fallback: keep temp path if rename fails


def _cloudinary_delete(file_field):
    """Delete a file from Cloudinary by its stored name (public_id without extension)."""
    if not _direct_upload_active() or not file_field:
        return
    name = file_field.name if hasattr(file_field, 'name') else str(file_field)
    if not name:
        return
    try:
        import cloudinary.uploader
        public_id = name.rsplit('.', 1)[0]  # strip extension
        ext = name.lower().rsplit('.', 1)[-1] if '.' in name else ''
        resource_type = 'video' if ext in ('mp4', 'webm', 'mov', 'avi') else 'image'
        cloudinary.uploader.destroy(public_id, resource_type=resource_type)
    except Exception:
        pass


@login_required
def admin_delete_popup(request, pk):
    popup = get_object_or_404(PopupAd, pk=pk)
    _cloudinary_delete(popup.image)
    _cloudinary_delete(popup.project_logo)
    popup.delete()
    from django.core.cache import cache
    cache.delete('api_popups')
    cache.delete('index_popups')
    return redirect('admin_popups')


@login_required
def admin_visitors(request):
    visitors = SiteVisitor.objects.all()[:100]
    return render(request, 'admin_panel/visitors.html', {'visitors': visitors})


@login_required
def admin_profile(request):
    from django.contrib.auth.forms import PasswordChangeForm
    from django.contrib.auth import update_session_auth_hash

    user = request.user
    msg = ''
    msg_type = ''

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'update_info':
            new_username = request.POST.get('username', '').strip()
            if new_username and new_username != user.username:
                from django.contrib.auth.models import User
                if User.objects.filter(username=new_username).exclude(pk=user.pk).exists():
                    msg = 'Username already taken.'
                    msg_type = 'error'
                else:
                    user.username = new_username
            user.first_name = request.POST.get('first_name', '')
            user.last_name = request.POST.get('last_name', '')
            user.email = request.POST.get('email', '')
            if msg_type != 'error':
                user.save()
                msg = 'Profile updated successfully.'
                msg_type = 'success'

        elif action == 'change_password':
            old_pw = request.POST.get('old_password', '')
            new_pw = request.POST.get('new_password1', '')
            confirm_pw = request.POST.get('new_password2', '')
            if not user.check_password(old_pw):
                msg = 'Current password is incorrect.'
                msg_type = 'error'
            elif new_pw != confirm_pw:
                msg = 'New passwords do not match.'
                msg_type = 'error'
            elif len(new_pw) < 6:
                msg = 'Password must be at least 6 characters.'
                msg_type = 'error'
            else:
                user.set_password(new_pw)
                user.save()
                update_session_auth_hash(request, user)
                msg = 'Password changed successfully.'
                msg_type = 'success'

        elif action == 'upload_photo':
            import os
            photo_public_id = request.POST.get('photo_public_id', '').strip()
            photo = request.FILES.get('photo')
            if photo_public_id and _cloudinary_active():
                # Direct upload already done — public_id stored by browser
                import time as _t
                msg = 'Photo uploaded successfully.'
                msg_type = 'success'
                request.session['photo_version'] = int(_t.time())
            elif photo:
                if photo.size > 10 * 1024 * 1024:
                    msg = 'Photo is too large. Please upload an image under 10 MB.'
                    msg_type = 'error'
                    photo = None
                if photo:
                    public_id = f'admin_photos/{user.username}'
                    if _cloudinary_active():
                        import cloudinary.uploader
                        cloudinary.uploader.upload(
                            photo,
                            public_id=public_id,
                            overwrite=True,
                            invalidate=True,
                            resource_type='image',
                        )
                    else:
                        from django.core.files.storage import default_storage
                        file_path = f'{public_id}.jpg'
                        try:
                            default_storage.delete(file_path)
                        except Exception:
                            pass
                        default_storage.save(file_path, photo)
                    msg = 'Photo uploaded successfully.'
                    msg_type = 'success'
                    import time as _t
                    request.session['photo_version'] = int(_t.time())

    photo_url = ''
    has_photo = False
    import os, time
    public_id = f'admin_photos/{user.username}'
    try:
        if _cloudinary_active():
            import cloudinary
            # Build URL from known public_id — guaranteed to match what was uploaded
            cloud_name = cloudinary.config().cloud_name
            ts = int(time.time())
            photo_url = f'https://res.cloudinary.com/{cloud_name}/image/upload/v{ts}/{public_id}.jpg'
            has_photo = True
        else:
            from django.core.files.storage import default_storage
            file_path = f'{public_id}.jpg'
            if default_storage.exists(file_path):
                photo_url = default_storage.url(file_path)
                has_photo = True
    except Exception as e:
        import logging
        logging.getLogger(__name__).error('Profile photo URL error: %s', e, exc_info=True)
        has_photo = False
        photo_url = ''

    return render(request, 'admin_panel/profile.html', {
        'msg': msg, 'msg_type': msg_type,
        'photo_url': photo_url, 'has_photo': has_photo,
        'cloudinary_active': _direct_upload_active(),
    })


@login_required
def admin_plots(request):
    # Brochure plots 1-121 excluding 30,31 (Marketing Office) = 119 plots
    all_plot_nos = [i for i in range(1, 122) if i not in (30, 31)]
    existing = set(VillaPlot.objects.values_list('villa_no', flat=True))
    missing = [i for i in all_plot_nos if i not in existing]
    if missing:
        VillaPlot.objects.bulk_create([VillaPlot(villa_no=i) for i in missing], ignore_conflicts=True)
    # Auto-expire reservations
    VillaPlot.objects.filter(status='reserved', reserved_until__lt=timezone.now()).update(
        status='available', reserved_by='', reserved_until=None)
    plots = VillaPlot.objects.filter(villa_no__in=all_plot_nos)
    sold = plots.filter(status='sold').count()
    reserved = plots.filter(status='reserved').count()
    nfs = plots.filter(status='not_for_sale').count()
    return render(request, 'admin_panel/plots.html', {
        'plots': plots,
        'sold': sold,
        'reserved': reserved,
        'nfs': nfs,
        'available': 119 - sold - reserved - nfs,
    })


@login_required
@require_POST
def admin_plot_update(request, villa_no):
    from datetime import timedelta
    plot, _ = VillaPlot.objects.get_or_create(villa_no=villa_no)
    import json as _json
    data = _json.loads(request.body)
    status = data.get('status', 'available')
    owner = data.get('owner_name', '').strip()
    notes = data.get('notes', '').strip()
    completion_pct = max(0, min(100, int(data.get('completion_pct', 0) or 0)))
    reserved_by = data.get('reserved_by', '').strip()
    reserve_days = int(data.get('reserve_days', 7) or 7)

    plot.status = status
    plot.notes = notes
    plot.owner_name = owner if status == 'sold' else ''
    if status == 'sold':
        plot.completion_pct = completion_pct

    if status == 'sold' and not plot.sold_at:
        plot.sold_at = timezone.now()
    elif status == 'reserved':
        plot.reserved_by = reserved_by
        plot.reserved_until = timezone.now() + timedelta(days=reserve_days)
        plot.sold_at = None
    elif status == 'available':
        plot.sold_at = None
        plot.reserved_by = ''
        plot.reserved_until = None
    else:  # not_for_sale
        plot.sold_at = None
        plot.reserved_by = ''
        plot.reserved_until = None

    plot.save()
    return JsonResponse({
        'success': True,
        'villa_no': villa_no,
        'status': plot.status,
        'owner': plot.owner_name,
        'completion_pct': plot.completion_pct,
        'reserved_until': plot.reserved_until.isoformat() if plot.reserved_until else None,
    })


# ─── Chatbot API ───

def chatbot_search(request):
    q = request.GET.get('q', '').strip().lower()
    all_qa = ChatbotQA.objects.filter(is_active=True)
    if not q:
        results = list(all_qa[:8])
    else:
        words = [w for w in q.split() if len(w) >= 2]
        matched = []
        for qa in all_qa:
            kws = qa.keyword_list()
            score = sum(1 for w in words if any(w in kw or kw in w for kw in kws))
            if score > 0:
                matched.append((score, qa))
        matched.sort(key=lambda x: -x[0])
        results = [qa for _, qa in matched[:6]]
    return JsonResponse({
        'results': [{'id': qa.id, 'question': qa.question} for qa in results]
    })


def chatbot_answer(request, qa_id):
    qa = get_object_or_404(ChatbotQA, pk=qa_id, is_active=True)
    answer = qa.answer
    if '{{PRICING_TABLE}}' in answer:
        types = FlatType.objects.filter(is_available=True).order_by('order')
        rows = []
        for ft in types:
            rows.append(
                f"• <strong>{ft.name}</strong> ({ft.bhk} BHK) — "
                f"Buildup: {ft.buildup_area} | Terrace: {ft.terrace_area} | "
                f"Price: ₹{ft.price:,.0f} (₹{ft.price_per_sqft:,.0f}/sq.ft)"
            )
        answer = answer.replace('{{PRICING_TABLE}}', '<br>'.join(rows) if rows else 'Contact us for latest pricing.')
    if '{{AVAILABLE_PLOTS}}' in answer:
        available = VillaPlot.objects.filter(status='available').count()
        total = VillaPlot.objects.count()
        answer = answer.replace('{{AVAILABLE_PLOTS}}', f'{available} out of {total}')
    response = {'question': qa.question, 'answer': answer}
    # After pricing overview, offer villa-type follow-up chips
    if qa.order == 1:
        villa_qas = ChatbotQA.objects.filter(order__in=range(101, 107), is_active=True).order_by('order')
        response['follow_up'] = [{'id': v.id, 'question': v.question} for v in villa_qas]
    return JsonResponse(response)


def chatbot_contact(request):
    project = ProjectInfo.load()
    return JsonResponse({
        'phone': project.phone,
        'email': project.email,
        'address': f"{project.address}, {project.city}, {project.state} - {project.pincode}".strip(', '),
        'website': project.website,
        'facebook': project.facebook,
        'instagram': project.instagram,
    })


# ─── Chatbot Admin ───

@login_required
def admin_chatbot(request):
    qas = ChatbotQA.objects.all()
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add':
            question = request.POST.get('question', '').strip()
            answer = request.POST.get('answer', '').strip()
            keywords = request.POST.get('keywords', '').strip()
            if question and answer and keywords:
                max_order = ChatbotQA.objects.aggregate(m=models.Max('order'))['m'] or 0
                ChatbotQA.objects.create(
                    question=question, answer=answer,
                    keywords=keywords, order=max_order + 1
                )
        elif action == 'delete':
            pk = request.POST.get('pk')
            ChatbotQA.objects.filter(pk=pk).delete()
        elif action == 'toggle':
            pk = request.POST.get('pk')
            qa = get_object_or_404(ChatbotQA, pk=pk)
            qa.is_active = not qa.is_active
            qa.save()
        return redirect('admin_chatbot')
    return render(request, 'admin_panel/chatbot.html', {'qas': qas})
