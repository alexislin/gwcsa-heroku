from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import RedirectView

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin/login$', 'django.contrib.auth.views.login', {'template_name': 'admin_login.html'}),
    url(r'^admin/logout$', 'django.contrib.auth.views.logout_then_login', {}),
    url(r'^admin/member_detail/(?P<id>\d+)$', 'gwcsa_heroku.admin_views.member_detail', name='member_detail'),
    url(r'^admin/members$', 'gwcsa_heroku.admin_views.members', name='members'),
    url(r'^admin/summaries$', 'gwcsa_heroku.admin_views.summaries', name='summaries'),
    url(r'^admin/workshifts$', 'gwcsa_heroku.admin_views.workshifts', name='workshifts'),

    # index page redirects to admin Members view
    url(r'^$', RedirectView.as_view(url='/admin/members')),
    url(r'^contact$', 'gwcsa_heroku.views.contact', name='contact'),
    url(r'^csv_xform$', 'gwcsa_heroku.views.csv_xform', name='csv_xform'),
    url(r'^signup_quiz$', 'gwcsa_heroku.views.signup_quiz', name='signup_quiz'),
    url(r'^workshift_selection$', 'gwcsa_heroku.views.workshift_selection', name='workshift_selection'),

    url(r'^ajax/get_available_dates_for_shift$', 'gwcsa_heroku.ajax.get_available_dates_for_shift', name='get_available_dates_for_shift'),
    url(r'^ajax/get_available_times_for_shift_date$', 'gwcsa_heroku.ajax.get_available_times_for_shift_date', name='get_available_times_for_shift_date'),

    url(r'^init/assigned_week$', 'gwcsa_heroku.init.init_assigned_week', name='init_assigned_week'),
    url(r'^email/assigned_week$', 'gwcsa_heroku.init.email_assigned_week', name='email_assigned_week'),
    url(r'^init/workshift$', 'gwcsa_heroku.init.init_workshift', name='init_workshift'),

    # Examples:
    # url(r'^gwcsa_heroku/', include('gwcsa_heroku.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
)
