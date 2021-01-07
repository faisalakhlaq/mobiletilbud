from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.storage import staticfiles_storage
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include
from django.utils.translation import gettext as _
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView

from core.views import change_language
from .sitemaps import StaticViewSitemap, MobilesSitemap, OffersSitemap

sitemaps = {
    'static': StaticViewSitemap,
    'mobiler': MobilesSitemap,
    'tilbud': OffersSitemap,
}

urlpatterns = [
    path('change_language/', change_language, name='change_language'),
    path('i18n/', include('django.conf.urls.i18n')),
    path("favicon.ico",
        RedirectView.as_view(url=staticfiles_storage.url("favicon.ico")),),
    path("robots.txt",
        TemplateView.as_view(template_name="core/robots.txt", 
        content_type="text/plain"),),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps},
        name='django.contrib.sitemaps.views.sitemap'),
]

urlpatterns += i18n_patterns(
    path('cookie-policy/', 
    TemplateView.as_view(template_name="core/cookie_policy.html"), 
    name='cookie-policy'),
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('', include('telecompanies.urls')),
    path('', include('mobiles.urls')),
    prefix_default_language=False,
)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'core.views.handler404'
handler500 = 'core.views.handler500'
handler403 = 'core.views.handler403'
handler400 = 'core.views.handler400'