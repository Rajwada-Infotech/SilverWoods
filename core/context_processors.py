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
