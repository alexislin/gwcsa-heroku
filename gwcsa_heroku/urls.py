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
    url(r'^admin/members/export$', 'gwcsa_heroku.admin_views.members_export', name='members_export'),
    url(r'^admin/sharelist$', 'gwcsa_heroku.admin_views.share_list', name='share_list'),
    url(r'^admin/summaries$', 'gwcsa_heroku.admin_views.summaries', name='summaries'),

    # index page redirects to admin Members view
    url(r'^$', RedirectView.as_view(url='/admin/members')),
    url(r'^contact$', 'gwcsa_heroku.views.contact', name='contact'),
    url(r'^csv_xform$', 'gwcsa_heroku.views.csv_xform', name='csv_xform'),
    url(r'^signup_quiz$', 'gwcsa_heroku.views.signup_quiz', name='signup_quiz'),

    # Examples:
    # url(r'^gwcsa_heroku/', include('gwcsa_heroku.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
)
