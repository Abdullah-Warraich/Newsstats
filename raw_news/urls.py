from django.contrib import admin
from django.urls import include, path

from raw_news.views import News_Update, dashboard_view, listing_view


urlpatterns = [
    path('dashboard/', dashboard_view, name='dashboard'),
    path('<int:id>/', listing_view, name='listing'),
    path('update/<int:id>/', News_Update.as_view(), name='update_news'),
]
