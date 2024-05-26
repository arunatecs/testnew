from django.shortcuts import redirect, render
import requests
from django.http import HttpResponseBadRequest
from fitbit_heartrate.models import FitbitIntegration
import os
import numpy as np
import ecg_plot
from django.conf import settings
import matplotlib
matplotlib.use('agg')

fitbit_integration = FitbitIntegration.objects.last()
FITBIT_CLIENT_ID = fitbit_integration.client_id
FITBIT_CLIENT_SECRET = fitbit_integration.client_secret
FITBIT_REDIRECT_URI = fitbit_integration.redirect_uri

def fitbit_authorize(request):
    # Redirect user to Fitbit for authorization
    auth_url = f'https://www.fitbit.com/oauth2/authorize?client_id={FITBIT_CLIENT_ID}&response_type=code&scope=activity%20heartrate%20location%20nutrition%20oxygen_saturation%20profile%20respiratory_rate%20settings%20sleep%20social%20temperature%20weight%20electrocardiogram&code_challenge=0z0P__in0XUbu2HHKmn6YcsFVWeI2QgKDwKTisi-FBc&code_challenge_method=S256'
    return redirect(auth_url)

def fitbit_callback(request):
    # Exchange authorization code for access token
    code = request.GET.get('code')
    token_url = 'https://api.fitbit.com/oauth2/token'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Basic MjNSVDNXOjYyYTZkM2Q1Y2ExNDU0YzM0NGIwNGU0NmFiYTc0MTQy'
    }
    data = {
        'client_id': FITBIT_CLIENT_ID,
        'client_secret': FITBIT_CLIENT_SECRET,
        'code': code,
        'grant_type': 'authorization_code',
        'code_verifier': '11220241710112202417101122024171011220241710'
    }
    response = requests.post(token_url, headers=headers, data=data)
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data['access_token']
        ecg_url = 'https://api.fitbit.com/1/user/-/ecg/list.json'
        params = {
            'afterDate': '2023-04-01',
            'offset': 0,
            'limit': 1,
            'sort': 'desc'
        }
        headers = {'Authorization': f'Bearer {access_token}'}
        ecg_response = requests.get(ecg_url, params=params, headers=headers)
        if ecg_response.status_code == 200:
            data = ecg_response.json()
            #ecg_readings = ecg_data["ecgReadings"][0]["waveformSamples"]
            
            waveform_samples = np.array([data["ecgReadings"][0]["waveformSamples"]])
            ecg_data = waveform_samples/100000  # milliVolt Conversion
            print(ecg_data.shape)
            ecg_plot.plot(ecg_data, sample_rate = 500 , title='fitbit')
            ecg_plot.save_as_png('fitbit_ecg2.png')
           
            return HttpResponseBadRequest("ECG chart displayed successfully")
        else:
            print(f"Error: {ecg_response.status_code} - {ecg_response.text}")
            return HttpResponseBadRequest("")
    else:
        return HttpResponseBadRequest("Failed to obtain access token from Fitbit")
