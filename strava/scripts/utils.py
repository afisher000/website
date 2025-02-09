import requests
from ..models import Activity, Split
from datetime import datetime

def fetch_athlete_id(request):
    # Query strava API for athlete
    endpoint = "https://www.strava.com/api/v3/athlete?"
    params = {'access_token':request.session.get('access_token')}
    response = requests.get(endpoint, params=params)

    # Error handle response
    if response.status_code != 200:
        print('Error requesting athlete id')
        return

    token_data = response.json()
    athlete_id = token_data.get('id')
    return athlete_id

def fetch_activities(athlete_id, access_token):
    print('Fetching activities...')

    # Query all athlete activities
    def query_activities(page):
        endpoint = 'https://www.strava.com/api/v3/activities?'
        params = {
            'access_token':access_token,
            'per_page':'200',
            'page':str(page),
            }
        return requests.get(endpoint, params=params)

    max_pages = 20
    for page in range(1, max_pages):
        response = query_activities(page)

        if response.status_code != 200:
            print('Failed to read activities')
            return

        activities = response.json()
        if len(activities)==0:
            break

        for activity in response.json():
            store_activity(activity, athlete_id)
            
    return 0

def store_activity(activity, athlete_id):
    activity_data = {
        'id':activity.get('id'),                
        'created_at': datetime.now(),
        'athlete_id': athlete_id,
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


def fetch_streams(athlete_id, access_token):
    activity_ids = Activity.objects.filter(has_stream=1).values_list('id', flat=True)

    # Download split IDs
    activity_ids_in_db = Split.objects.filter(athlete_id=athlete_id).values_list('activity_id', flat=True).distinct()

    print(f'Storing splits for {len(activity_ids)-len(activity_ids_in_db)} activities')

    def download_stream(activity_id):
        endpoint = f"https://www.strava.com/api/v3/activities/{activity_id}/streams?"
        params = {
            'access_token':access_token,
            'keys':','.join(['distance','latlng','time','altitude', 'heartrate', 'cadence']),
            'key_by_type':'true'
            }
        return requests.get(endpoint, params=params)


    # Loop over activities, downloading if not in database
    for activity_id in activity_ids:
        if activity_id not in activity_ids_in_db:
            response = download_stream(activity_id)

            if response.status_code == 200:
                stream = response.json()
                store_splits(athlete_id, activity_id, stream)

            elif response.status_code == 404:
                print(f'\tFailed with error 404, no stream exists for activity {activity_id}')
                Activity.objects.filter(id=activity_id).update(has_stream=0)

            # status_code when out of queries??
            else:
                print(response)
                
        
    print(f'\tFinished storing splits')
    return 0

def store_splits(athlete_id, activity_id, stream):

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