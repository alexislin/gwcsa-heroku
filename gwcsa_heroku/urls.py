from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # url(r'^admin/', include(admin.site.urls)),

    url(r'^$', 'gwcsa_heroku.views.index', name='index'),

    url(r'^workshift_selection$', 'gwcsa_heroku.views.workshift_selection', name='workshift_selection'),

    # Examples:
    # url(r'^gwcsa_heroku/', include('gwcsa_heroku.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
)
