# home/urls.py
from django.conf.urls import url

from home import views

app_name = 'home'
urlpatterns = [
    url(r'upload/csv/$', views.upload_csv, name='upload-csv'),
]
