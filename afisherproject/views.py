from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
import os
from urllib.parse import urlencode
import requests
import logging
from django.contrib.auth.decorators import login_required
from datetime import datetime


logger = logging.getLogger(__name__)

def website_home(request):
    return render(request, 'website_home.html')


def website_about(request):
    return render(request, 'website_about.html')