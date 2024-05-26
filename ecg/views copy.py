from django.shortcuts import redirect,render
import requests
from django.http import HttpResponseBadRequest
from fitbit_heartrate.models import FitbitIntegration
from django.http import JsonResponse
import json
import numpy as np
import matplotlib.pyplot as plt
import ecg_plot

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
    print(f'code : {code}')
    token_url = 'https://api.fitbit.com/oauth2/token'
    headers = {'Content-Type': 'application/x-www-form-urlencoded',
                'Authorization':'Basic MjNSVDNXOjYyYTZkM2Q1Y2ExNDU0YzM0NGIwNGU0NmFiYTc0MTQy'}
    data = {
        'client_id': FITBIT_CLIENT_ID,
        'client_secret': FITBIT_CLIENT_SECRET,
        'code': code,
        'grant_type': 'authorization_code',
        'code_verifier':'11220241710112202417101122024171011220241710'    }
    print(f'data  : {data}')
    response = requests.post(token_url, headers=headers, data=data)
    print(response.content)
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data['access_token']
        print(f'access_token:{access_token}')
        
       
       
        ecg_url = 'https://api.fitbit.com/1/user/-/ecg/list.json'
        
        params = {
    
                    'afterDate': '2023-04-01',
                    #'beforeDate': '2023-12-31',
                    'offset':0,
                    'limit':1,
                    'sort': 'desc'
                    }
        
        headers = {'Authorization': f'Bearer {access_token}'}
        ecg_response = requests.get(ecg_url, params=params, headers=headers)
        #print(ecg_response.content)
        ecg_data = ecg_response.json()
        #print(f'ecgdaata :::::::::::{ecg_data}')
        #print("hello")
        #print(ecg_data)
        print("Request URL:", ecg_response.url)

        # Check if the response was successful (status code 200)
        if ecg_response.status_code == 200:
            # Request was successful, parse and use the response data
            data = ecg_response.json()
            #print(data)
            ecg_readings=ecg_response.content
            #print(ecg_readings)
            waveform_samples = data["ecgReadings"][0]["waveformSamples"]
            print('hello')    
            print(waveform_samples)
            plt.figure(figsize=(10, 5))
            time_points = np.arange(len(waveform_samples))  # Generate time points for each sample
            plt.scatter(time_points, waveform_samples, color='black')  # Scatter plot for ECG data points
            plt.plot(time_points, waveform_samples, color='black', alpha=0.3)  # Connect the points with a line
            plt.title('Single Lead ECG', fontsize=16)
            plt.xlabel('Time (s)', fontsize=14)
            plt.ylabel('Amplitude (mV)', fontsize=14)
            plt.grid(True)
    
            plt.show()
            return HttpResponseBadRequest("ECG Chart displayed successfully")
        else:
            # Request failed, print error message

            print(f"Error: {ecg_response.status_code} - {ecg_response.text}")
            return HttpResponseBadRequest("")
       
    else:
        return HttpResponseBadRequest("Failed to obtain access token from Fitbit")

