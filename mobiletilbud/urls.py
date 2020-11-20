from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import path, include
from django.utils.translation import gettext as _

from core.views import change_language


urlpatterns = [
    path('change_language/', change_language, name='change_language'),
    path('i18n/', include('django.conf.urls.i18n')),
]

urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('', include('telecompanies.urls')),
    prefix_default_language=False,
)
