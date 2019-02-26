from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^create_checks/$', views.create_checks),
    url(r'^new_checks/$', views.get_checks_list),
    url(r'^check/$', views.get_check),
]
