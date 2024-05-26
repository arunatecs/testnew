import numpy as np
import matplotlib.pyplot as plt
import requests
from django.shortcuts import redirect, render
from django.http import HttpResponseBadRequest
from fitbit_heartrate.models import FitbitIntegration
from breathrate.models_mongo import Breathrate
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
from datetime import datetime, timedelta

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
    print('ggggg')
    print(response.content)
    if response.status_code == 200:
       
        start_date = datetime(2023,12, 1)
        end_date = datetime(2023, 12, 31)

        # List to store dates with available breath rate data
        dates_with_data = []

        # Iterate through each date in the specified range
        current_date = start_date
        while current_date <= end_date:
            token_data = response.json()
            access_token = token_data['access_token']
            print(access_token)
            headers = {'Authorization': f'Bearer {access_token}'}
        #ecg_response = requests.get(ecg_url, params=params, headers=headers)
        #date = '2024-02-05'
        #breathrate_url = f'https://api.fitbit.com/1/user/-/br/date/2023-10-04.json'
# Specify the date range for which you want to check breath rate data
        
            date_str = current_date.strftime('%Y-%m-%d')
            breathrate_url = f'https://api.fitbit.com/1/user/-/br/date/2021-11-09/all.json'
            
            headers = {'Authorization': f'Bearer {access_token}'}
            breathrate_response = requests.get(breathrate_url, headers=headers)
            print(breathrate_response.content)
            if breathrate_response.status_code == 200:
                data = breathrate_response.json()
                print(data) 
                breathrate_readings = data.get('br', [])
                
                if breathrate_readings:
                    # If data is available, add the date to the list
                    dates_with_data.append(date_str)
            else:
                print(f"Error fetching breath rate data for {date_str}: {breathrate_response.status_code}")
            
            # Move to the next date
            current_date += timedelta(days=1)

        # Print the dates with available data
        print("Dates with available breath rate data:")
        for date in dates_with_data:
            print(date)
            # Move to the next date
            current_date += timedelta(days=1)
def breathrate_list(request):
    # Retrieve breathrate readings from MongoDB using Djongo
    #breathrate_readings = list(breathrate.objects.values()) # all records\
    breathrate_readings = list(Breathrate.objects.order_by('-timestamp')[:5].values())  # recent 5 records
    

    # Convert ObjectId to string representation for each record
    for breathrate_reading in breathrate_readings:
        breathrate_reading['id'] = str(breathrate_reading.pop('_id'))  # Convert _id to id and ensure it's a string

    return render(request, 'breathrate.html', {'breathrate_readings': breathrate_readings})

def breathrate_chart(request,breathrate_id):
    
    print('hello')
    print(breathrate_id)
    breathrate_object_id = ObjectId(breathrate_id)
    print(breathrate_id)    
        # Retrieve breathrate document from MongoDB using Djongo
    breathrate_reading = Breathrate.objects.filter(_id=breathrate_object_id).first()


    print(breathrate_reading)
    if breathrate_reading:
        value = breathrate_reading.value 
        waveform_samples = np.array(value)
        breathrate_data = waveform_samples / 10000  # milliVolt Conversion

        plt.figure(figsize=(20, 8))
        x_ticks = np.arange(0, 31, step=0.1)
        y_ticks = np.arange(-2, 2, step=0.1)

        # Add vertical grid lines
        for x in x_ticks:
            plt.axvline(x, color='red', linestyle='--', linewidth=0.5)

        # Add horizontal grid lines
        for y in y_ticks:
            plt.axhline(y, color='red', linestyle='--', linewidth=0.5)

        num_samples = len(breathrate_data)
        time = np.linspace(0, 30, num_samples)  # Assuming 30 seconds duration
        plt.plot(time, breathrate_data)
        plt.title('breathrate Chart')
        plt.xlabel('Time (seconds)')
        plt.ylabel('Voltage (mV)')
        plt.grid(True, which='both', linestyle='-', linewidth=1, color='red')
        plt.xticks(np.arange(0, 31, step=1))
        plt.xlim(0, 30)  # Set x-axis limit from 0 to 30 seconds

        # Save the plot
        image_path = 'breathrate.png'
        plt.savefig(image_path)

        # Convert plot to HTTP response
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)

        # Clear the plot from memory
        plt.close()

        # Return the image as an HTTP response
        return HttpResponse(buffer.getvalue(), content_type='image/png')
    else:
        return HttpResponse('breathrate not found')
def home(request):
    return render(request, 'home.html')

def dashboard(request):
    return render(request, 'dashboard.html')
  