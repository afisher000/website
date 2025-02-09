from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.strava_home, name='strava_home'),
    path('auth/', views.strava_auth, name='strava_auth'),
    path('callback/', views.strava_callback, name='strava_callback'),
    path('fetch/', views.strava_fetch, name='strava_fetch'),
    path('index/', views.strava_index, name='strava_index'),
    path('activity/<int:activity_id>/', views.strava_activity, name='strava_activity'),
]
