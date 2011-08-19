from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^(?P<key>[a-f0-9]{40})$','sharepic.views.authuser'),
    (r'^newshare/','sharepic.views.newshare'),
    (r'^send_key/$','sharepic.views.send_key'),
    (r'^request_key/$','sharepic.views.request_key'),
    (r'^remove/(?P<uri>\d*)$','sharepic.views.remove_image'),
    (r'^remove/(?P<uri>.*)$','sharepic.views.remove_share'),
    (r'^logout/$','sharepic.views.logout'),
    (r'^upload/progress/$', 'sharepic.views.upload_progress', {}, 'upload_progress'),
    (r'^(?P<uri>.*)$', 'sharepic.views.showshare'),
)