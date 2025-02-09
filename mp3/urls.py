from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.mp3_home, name='mp3_home'),
    path('search/', views.mp3_search, name='mp3_search'),
    path('create/', views.mp3_create, name='mp3_create'),
    path('track/<int:track_id>/', views.mp3_show_song, name='mp3_show_song'),
    path('download/', views.mp3_download, name='mp3_download')
]