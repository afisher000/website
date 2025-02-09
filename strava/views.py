from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
import os
from urllib.parse import urlencode
import requests
import logging
from django.contrib.auth.decorators import login_required
from datetime import datetime
from .models import Activity, Split
from django.core.paginator import Paginator
from .scripts.utils import fetch_athlete_id, fetch_activities, fetch_streams
logger = logging.getLogger(__name__)

def strava_sync(request):
    return render(request, 'strava_sync.html')

def strava_activity(request):
    return redirect('strava_index')

def strava_index(request):
    # Get all Strava activities, ordered by 'date' in descending order (reverse chronological order)
    activities = Activity.objects.all().order_by('-start_date')  # Adjust 'date' field name if needed
    
    paginator = Paginator(activities, 10)
    
    # Get the current page number from the request
    page_number = request.GET.get('page')  # This gets the 'page' parameter from the query string
    page_obj = paginator.get_page(page_number)  # Get the page of activities

    # Pass the page_obj to the template
    return render(request, 'strava_index.html', {'page_obj': page_obj})


def strava_home(request):
    tokens = ['athlete_id', 'access_token']
    session_tokens = {t:request.session.get(t, None) for t in tokens}
    return render(request, 'strava_home.html', session_tokens)


def strava_auth(request):
    # Build url for strava authentification
    auth_endpoint = 'https://www.strava.com/oauth/authorize?'
    params = {
            'client_id':os.environ['STRAVA_CLIENT_ID'],
            'redirect_uri':'http://localhost:8000/strava/callback/', 
            'response_type':'code',
            'scope':'activity:read_all'
            }
    auth_url = f"{auth_endpoint}{urlencode(params)}"
    logger.info('Redirecting to Strava website for authentification')
    return redirect(auth_url)


def strava_callback(request):
    # Ensure session parameters
    code = request.GET.get('code')
    if not code:
        return JsonResponse({'error': 'No code received'}, status=400)

    # Respond with client secret
    token_endpoint = 'https://www.strava.com/oauth/token?'
    params = {
        'client_id':os.environ['STRAVA_CLIENT_ID'],
        'client_secret':os.environ['STRAVA_CLIENT_SECRET'],
        'code':request.GET.get('code'),
        'grant_type':'authorization_code'
        }
    response = requests.post(token_endpoint, params=params)
    
    # Error handle response
    if response.status_code != 200:
        return JsonResponse({"error": "Failed to exchange code for access token"}, status=400)
    
    # Read access token
    token_data = response.json()
    access_token = token_data.get('access_token')

    # Fetch athlete id
    athlete_id = fetch_athlete_id()
    if athlete_id is None:
        return JsonResponse({"error": "Failed to fetch athlete_id"}, status=400)
    
    # Fetch activities
    status = fetch_activities(athlete_id, access_token)
    if status is None:
        return JsonResponse({"error": "Failed to read activities"}, status=400)

    # Fetch streams
    status = fetch_streams(athlete_id, access_token)
    if status is None:
        return JsonResponse({"error": "Failed to read stream"}, status=400)

    return render(request, 'strava_index.html')
    

    
    



    
