from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponsePermanentRedirect
from django.templatetags.static import static as static_url
from django.conf import settings
from django.conf.urls.static import static


def favicon(request):
    # Resolved per request: the hashed static manifest only exists after collectstatic
    return HttpResponsePermanentRedirect(static_url("favicon.ico"))

urlpatterns = [
    path("favicon.ico", favicon),
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
