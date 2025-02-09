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

logger = logging.getLogger(__name__)

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
    if response.status_code == 200:
        token_data = response.json()
        request.session['access_token'] = token_data.get('access_token')
        request.session['refresh_token'] = token_data.get('refresh_token')
        request.session['expires_at'] = token_data.get('expires_at')

        return redirect(reverse('strava_home'))
    
    return JsonResponse({"error": "Failed to exchange code for access token"}, status=400)
    

def strava_fetch(request):
    if not request.session.get('athlete_id'):
        error = fetch_athlete_id(request)
        if error is not None:
            return error

    # Get activities
    error = fetch_activities(request)
    if error is not None:
        return error
    
    error = fetch_streams(request)
    if error is not None:
        return error
    
    return redirect(reverse('strava_home'))

def fetch_athlete_id(request):
    # Query strava API for athlete
    endpoint = "https://www.strava.com/api/v3/athlete?"
    params = {'access_token':request.session.get('access_token')}
    response = requests.get(endpoint, params=params)

    # Error handle response
    if response.status_code == 200:
        token_data = response.json()
        request.session['athlete_id'] = token_data.get('id')
        print(f'Athlete id = {token_data.get('id')}')
        return

    return JsonResponse({"error": "Failed to query athlete_id"}, status=400)


def fetch_activities(request):
    print('Fetching activities...')
    def store_activity(activity):
        activity_data = {
            'id':activity.get('id'),                
            'created_at': datetime.now(),
            'athlete_id': request.session.get('athlete_id'),
            'elapsed_time': activity.get('elapsed_time'),
            'name': activity.get('name', ''),
            'sport_type': activity.get('sport_type'),
            'total_elevation_gain': activity.get('total_elevation_gain'),
            'start_date': datetime.fromisoformat(activity['start_date'][:-1]).strftime('%Y-%m-%d %H:%M:%S'),
            'start_lat': activity.get('start_lat'),
            'start_lng': activity.get('start_lng'),
            'average_speed': activity.get('average_speed'),
            'average_cadence': activity.get('average_cadence'),
            'distance': activity.get('distance'),
            'has_stream': activity.get('has_stream', 0),
        }

        if not Activity.objects.filter(id=activity_data['id']).exists():
            print(f'\tStoring activity {activity.get('id')}...')
            Activity.objects.create(**activity_data)
        return


    # Query all athlete activities
    def query_activities(page):
        endpoint = 'https://www.strava.com/api/v3/activities?'
        params = {
            'access_token':request.session.get('access_token'),
            'per_page':'200',
            'page':str(page),
            }
        return requests.get(endpoint, params=params)

    max_pages = 20
    for page in range(1, max_pages):
        response = query_activities(page)

        # Error handle for each page query
        if response.status_code == 200:
            activities = response.json()
            if len(activities)==0:
                break

            for activity in response.json():
                store_activity(activity)
        else:
            return JsonResponse({"error": "Failed to read activities"}, status=400)

    print(f'\tFinished storing activities, queried {page} pages')
    return
    
def fetch_streams(request):
    activity_ids = Activity.objects.filter(has_stream=1).values_list('id', flat=True)

    # Download split IDs
    athlete_id = request.session.get('athlete_id')
    activity_ids_in_db = Split.objects.filter(athlete_id=athlete_id).values_list('activity_id', flat=True).distinct()

    print(f'Storing splits for {len(activity_ids)-len(activity_ids_in_db)} activities')

    def download_stream(activity_id):
        endpoint = f"https://www.strava.com/api/v3/activities/{activity_id}/streams?"
        params = {
            'access_token':request.session.get('access_token'),
            'keys':','.join(['distance','latlng','time','altitude', 'heartrate', 'cadence']),
            'key_by_type':'true'
            }
        return requests.get(endpoint, params=params)

    def store_splits(activity_id, stream):
        athlete_id = request.session.get('athlete_id')

        if 'time' in stream:
            time_data = stream.get('time')['data']
            distance_data = stream.get('distance')['data']
            Nsamples = len(time_data)
        else:
            print(f'No time data, skipping stream {activity_id}')

        if 'cadence' in stream:
            cadence_data = stream.get('cadence')['data']
        else:
            cadence_data = [0.0]*Nsamples

        if 'heartrate' in stream:
            hr_data = stream.get('heartrate')['data']
        else:
            hr_data = [0.0]*Nsamples

        if 'altitude' in stream:
            altitude_data = stream.get('altitude')['data']
        else:
            altitude_data = [0.0]*Nsamples

        if 'latlng' in stream:
            latlng_data = stream.get('latlng')['data']
            [lat_data, lng_data] = list(zip(*latlng_data))
        else:
            lat_data = [0.0]*Nsamples
            lng_data = [0.0]*Nsamples

        # Define split length in meters
        split_distance = 100

        # Correct outlier activity errors
        if distance_data[0]>split_distance:
            distance_data[0] = 0

        # Initialize "prev" values
        prev_split_number = 1
        prev_time = time_data[0]
        prev_distance = distance_data[0]
        prev_altitude = altitude_data[0]

        # Loop over stream samples
        print(f'\tCreating splits for activity {activity_id}')
        for j in range(Nsamples):
            
            if distance_data[j]/split_distance>prev_split_number:

                # Build new data
                split_data = {
                    'activity_id':activity_id,
                    'athlete_id':athlete_id, 
                    'speed':(distance_data[j]-prev_distance)/(time_data[j]-prev_time),
                    'grade':(altitude_data[j]-prev_altitude)/(distance_data[j]-prev_distance),
                    'lat':lat_data[j],
                    'lng':lng_data[j],
                    'split_number':prev_split_number,
                    'altitude':altitude_data[j],
                    'hr':hr_data[j],
                    'cadence':cadence_data[j]
                }
                Split.objects.create(**split_data)
                

                # Update prev values
                prev_time = time_data[j]
                prev_distance = distance_data[j]
                prev_altitude = altitude_data[j]
                prev_split_number += 1

        return

    # Loop over activities, downloading if not in database
    for activity_id in activity_ids:
        if activity_id not in activity_ids_in_db:
            response = download_stream(activity_id)
            if response.status_code == 200:
                stream = response.json()
                store_splits(activity_id, stream)
            elif response.status_code == 404:
                print(f'\tFailed with error 404, no stream exists for activity {activity_id}')
                Activity.objects.filter(id=activity_id).update(has_stream=0)
            else:
                print(response)
                return JsonResponse({"error": "Failed to read stream"}, status=400)
        
    print(f'\tFinished storing splits')
    return
