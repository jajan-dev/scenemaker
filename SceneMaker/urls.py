from django.conf.urls import patterns, include, url
import views
from django.contrib import admin
admin.autodiscover()

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'SceneMaker.views.home', name='home'),
    url(r'^$', views.index),
    url(r'login/^$', views.login),
    url(r'logout/^$', views.logout),
    url(r'signup/^$', views.signup),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include('API.urls', namespace='API')),
)