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


def site_phone(request):
    """Phone number for the floating call button shown on every public page."""
    from django.core.cache import cache
    phone = cache.get('site_phone')
    if phone is None:
        from .models import ProjectInfo
        phone = ProjectInfo.load().phone or DEFAULT_SITE_PHONE
        cache.set('site_phone', phone, 300)
    return {'site_phone': phone}
