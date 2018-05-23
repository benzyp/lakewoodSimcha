"""
Definition of urls for LakewoodSimcha.
"""

from datetime import datetime
from django.conf.urls import url
import django.contrib.auth.views

import app.forms
import app.views
import app.admin_views

# Uncomment the next lines to enable the admin:
from django.conf.urls import include
from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    # Examples:
    url(r'^$', app.views.home, name='home'),
    url(r'^book/(?P<booking>[a-z]+)', app.views.book, name='book'),
    url(r'^verify/phone', app.views.verify_phone, name='verify_phone'),
    url(r'^venue/page/(?P<pk>\d+)', app.views.venue_page, name='venue_page'),
    url(r'^help', app.views.help, name='help'),
    url(r'^contact$', app.views.contact, name='contact'),
    url(r'^about', app.views.about, name='about'),
    url(r'^login/$',
        django.contrib.auth.views.login,
        {
            'template_name': 'app/login.html',
            'authentication_form': app.forms.BootstrapAuthenticationForm,
            'extra_context':
            {
                'title': 'Log in',
                'year': datetime.now().year,
            }
        },
        name='login'),
    url(r'^logout$',
        django.contrib.auth.views.logout,
        {
            'next_page': '/',
        },
        name='logout'),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    #admin_views
    url(r'^events/(?P<pk>\d+)', app.admin_views.event_list, name='event_list'),
    url(r'^event/(?P<pk>\d+)/delete/$', app.admin_views.event_delete, name='event_delete'),
    url(r'^event/(?P<pk>\d+)/update/$', app.admin_views.event_update, name='event_update'),
]
