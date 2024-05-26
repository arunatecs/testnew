import numpy as np
import matplotlib.pyplot as plt
import requests
from django.shortcuts import redirect, render
from django.http import HttpResponseBadRequest
from fitbit_heartrate.models import FitbitIntegration
import os
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
            'afterDate': '2023-08-04',
            'offset': 0,
            'limit': 1,
            'sort': 'asc'
        }
        headers = {'Authorization': f'Bearer {access_token}'}
        ecg_response = requests.get(ecg_url, params=params, headers=headers)
    
        if ecg_response.status_code == 200:
            data = ecg_response.json()
            waveform_samples = np.array(data["ecgReadings"][0]["waveformSamples"])
            ecg_data = waveform_samples / 10000  # milliVolt Conversion
            
            # Plot ECG data
            plt.figure(figsize=(20, 8))
            x_ticks = np.arange(0, 31, step=0.1) 
            #plt.xticks(x_ticks)
     
            y_ticks = np.arange(-2, 2, step=0.1)  # Adjust the step value for more grid lines

                    # Add vertical grid lines
            for x in x_ticks:
                        plt.axvline(x, color='red', linestyle='--', linewidth=0.5)

                    # Add horizontal grid lines
            for y in y_ticks:
                        plt.axhline(y, color='red', linestyle='--', linewidth=0.5)
            num_samples = len(ecg_data)
            time = np.linspace(0, 30, num_samples)  # Assuming 30 seconds duration
            plt.plot(time, ecg_data)
            plt.title('ECG Chart')
            plt.xlabel('Time (seconds)')
            plt.ylabel('Voltage (mV)')
            plt.grid(True, which='both', linestyle='-', linewidth=1,color='red')
            plt.xticks(np.arange(0, 31, step=1))
            plt.xlim(0, 30)  # Set x-axis limit from 0 to 30 seconds
            #plt.show()
            image_path = 'ecg.png'
            plt.savefig(image_path)
            return HttpResponseBadRequest("ECG chart displayed successfully")
    
        else:
            # Handle error response
            print(f"Error: {ecg_response.status_code} - {ecg_response.text}")
            return HttpResponseBadRequest("Failed to obtain ECG data from Fitbit")
    else:
        # Handle error response
        print(f"Error: {response.status_code} - {response.text}")
        return HttpResponseBadRequest("Failed to obtain access token from Fitbit")
