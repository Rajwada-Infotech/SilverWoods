import os
import time
from django.conf import settings


def admin_photo(request):
    """Inject admin_photo_url into every template context."""
    if not request.user.is_authenticated:
        return {'admin_photo_url': ''}
    try:
        public_id = f'admin_photos/{request.user.username}'
        # Use session-stored version so cache busts immediately after upload
        v = request.session.get('photo_version', int(time.time()))
        if os.environ.get('CLOUDINARY_URL'):
            import cloudinary
            cloud_name = cloudinary.config().cloud_name
            url = f'https://res.cloudinary.com/{cloud_name}/image/upload/v{v}/{public_id}.jpg'
        else:
            url = f'{settings.MEDIA_URL}{public_id}.jpg?v={v}'
        return {'admin_photo_url': url}
    except Exception:
        return {'admin_photo_url': ''}


DEFAULT_SITE_PHONE = '+91 7411781881'
DEFAULT_SITE_WHATSAPP = '+91 9831405414'


def site_phone(request):
    """Phone and WhatsApp numbers for the floating contact buttons on every public page."""
    from django.core.cache import cache
    numbers = cache.get('site_phone')
    if numbers is None:
        from .models import ProjectInfo
        project = ProjectInfo.load()
        numbers = {
            'site_phone': project.phone or DEFAULT_SITE_PHONE,
            'site_whatsapp': project.whatsapp or DEFAULT_SITE_WHATSAPP,
        }
        cache.set('site_phone', numbers, 300)
    return numbers
