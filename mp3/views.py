from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
import os
from urllib.parse import urlencode
import requests
import logging
from django.contrib.auth.decorators import login_required
from datetime import datetime
from .forms import SubmissionForm
from .models import Track
from .scripts import youtube_download

def mp3_home(request):
    return render(request, 'mp3_home.html')

def mp3_download(request):
    tracks_to_download = Track.objects.filter(downloaded=False)

    for track in tracks_to_download:
        # Download
        try:
            youtube_download(track)

            # Update database
            track.downloaded = True
            track.save()
        except Exception as e:
            print('\tDownload failed! Skipping...')

    return redirect('mp3_search')


def mp3_search(request):
    if not request.GET.get('query'):
        prev_filters = {'attribute': 'songTerm', 'query': ''}
        songs = []
    else:
        # Parse form data
        attribute = request.GET.get('attribute', 'songTerm')  # Default to 'songTerm' if not provided
        query = request.GET.get('query', '')

        prev_filters = {
            'attribute': attribute,
            'query': query,
        }

        # iTunes API request
        endpoint = "https://itunes.apple.com/search?"
        params = {
            'limit': 30,
            'entity': 'song',
            'attribute': attribute,
            'term': query,
        }

        # Fetch the data from the iTunes API
        response = requests.get(endpoint, params=params)

        # Check if the response is valid and extract the results
        if response.status_code == 200:
            songs = response.json().get('results', [])
        else:
            songs = []

    # Get tracks yet to be downloaded
    tracks = Track.objects.filter(downloaded=False)

    return render(request, 'mp3_search.html', {
        'prevFilters': prev_filters,
        'songs': songs,
        'tracks': tracks,
    })

def mp3_show_song(request, track_id):
    # Define the iTunes API endpoint and parameters
    endpoint = "https://itunes.apple.com/lookup?"
    params = {
        'id': track_id,
        'entity': 'song',
    }

    # Make the HTTP request to the iTunes API
    response = requests.get(endpoint, params=params)
    song = response.json().get('results', [])[0]  # Get the first result (if any)
    
    form = SubmissionForm()
    form.fields['artist'].initial = song.get('artistName', 'None')
    form.fields['name'].initial = song.get('trackName', 'None')
    
    # Pass the song data to the template
    return render(request, 'mp3_create.html', {'form':form})

def mp3_create(request, song=None):
    if request.method=='POST':
        form = SubmissionForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['url']
            artist = form.cleaned_data['artist']
            name = form.cleaned_data['name']

            if Track.objects.filter(artist=artist, name=name).exists():
                form.add_error(None, 'This song already exists in the database.')
                return render(request, 'mp3_create.html', {'form':form})

            track = Track(url=url, artist=artist, name=name, downloaded=False)
            track.save()
            return render(request, 'mp3_home.html')
        else:
            pass
    else:
        form = SubmissionForm()

    return render(request, 'mp3_create.html', {'form':form})


