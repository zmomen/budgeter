# reports/urls.py
from django.conf.urls import url

from reports import views

app_name = 'reports'
urlpatterns = [
    url(r'^reports/$', views.reports, name='reports'),
    url(r'^reports/(?P<year>\d+)/(?P<month>\d+)/$', views.reports, name='by_month_id'),
    # url(r'^reports/(?P<year>\d+)/(?P<month>\d+)/$', views.income_reports, name='income'),
    url(r'^reports/category/(?P<cat_id>\d+)/$', views.reports, name='by_category_id'),
]
