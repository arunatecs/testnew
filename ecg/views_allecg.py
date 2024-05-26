import numpy as np
import matplotlib.pyplot as plt
import requests
from django.shortcuts import redirect, render
from django.http import HttpResponseBadRequest
from fitbit_heartrate.models import FitbitIntegration
from ecg.models_mongo import Ecg
import os
from django.conf import settings
import matplotlib
matplotlib.use('agg')
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from pymongo import MongoClient
from bson.objectid import ObjectId
from django.http import HttpResponse
from io import BytesIO

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
            'afterDate': '2023-08-02',
            'offset': 0,
            'limit': 5,
            'sort': 'asc'
        }
        headers = {'Authorization': f'Bearer {access_token}'}
        ecg_response = requests.get(ecg_url, params=params, headers=headers)
    
        if ecg_response.status_code == 200:
            data = ecg_response.json()
            print(data)
            ecg_readings = data.get('ecgReadings', [])
            for reading in ecg_readings:
                waveform_samples = reading.get("waveformSamples", [])
                # Save each reading to the database
                ecg = Ecg.objects.create(value=waveform_samples)
            
            return HttpResponseBadRequest("ECG data saved successfully")
    
        else:
            # Handle error response
            print(f"Error: {ecg_response.status_code} - {ecg_response.text}")
            return HttpResponseBadRequest("Failed to obtain ECG data from Fitbit")
    else:
        # Handle error response
        print(f"Error: {response.status_code} - {response.text}")
        return HttpResponseBadRequest("Failed to obtain access token from Fitbit")
def ecg_list(request):
    # Retrieve ECG readings from MongoDB using Djongo
    ecg_readings = list(Ecg.objects.values()) # all records\
    

    # Convert ObjectId to string representation for each record
    for ecg_reading in ecg_readings:
        ecg_reading['id'] = str(ecg_reading.pop('_id'))  # Convert _id to id and ensure it's a string

    return render(request, 'ecg_list.html', {'ecg_readings': ecg_readings})

def ecg_chart(request, ecg_id):
    print('hello')
    print(ecg_id)
    client = MongoClient('mongodb://admin:password@localhost:27017/?authSource=admin&authMechanism=DEFAULT')
    db = client['django1'] 
    collection = db['ecg_ecg']  

    
    document = collection.find_one({'_id': ObjectId(ecg_id)})
    
    if document:
         value = document.get('value')
         print(value)
    
    waveform_samples = np.array(value)
    ecg_data = waveform_samples / 10000  # milliVolt Conversion

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
    plt.show()
    image_path = 'ecg.png'
    plt.savefig(image_path)
    #return JsonResponse(data)
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    
    # Return the image as an HTTP response
    return HttpResponse(buffer.getvalue(), content_type='image/png')