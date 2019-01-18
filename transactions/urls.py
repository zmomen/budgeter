# transactions/urls.py
from django.conf.urls import url

from transactions import views

app_name = 'transactions'
urlpatterns = [
    url(r'^categories/$', views.view_categories, name='view-categories'),
    url(r'^categories/(?P<action>\w+)/(?P<id>\d+)/$', views.edit_category, name='edit-category'),
    url(r'^reports/$', views.reports, name='reports'),
    url(r'^reports/(?P<year>\d+)/(?P<month>\d+)/$', views.reports, name='by_month_id'),
    url(r'^reports/category/(?P<cat_id>\d+)/$', views.reports, name='by_category_id'),
    url(r'^search/$', views.search, name='search'),
    url(r'^edit-transaction/(?P<id>\d+)/$', views.edit_transaction, name='edit-transaction'),
]
