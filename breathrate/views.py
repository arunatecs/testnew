import numpy as np
import matplotlib.pyplot as plt
import requests
from django.shortcuts import redirect, render
from django.http import HttpResponseBadRequest
from fitbit_heartrate.models import FitbitIntegration
from breathrate.models_mongo import Breathrate,Activity,HeartRate
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
from datetime import datetime

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
    
    print(response.content)
    if response.status_code == 200:
       
        
        token_data = response.json()
        access_token = token_data['access_token']
        print(access_token)
        headers = {'Authorization': f'Bearer {access_token}'}
        
        date = '2024-02-05'
        breathrate_url = f'https://api.fitbit.com/1/user/-/br/date/{date}.json'
       
       
        breathrate_response = requests.get(breathrate_url, headers=headers)
        print('BreathRate Value : ')

        print(breathrate_response.content)
        if breathrate_response.status_code == 200:
            data = breathrate_response.json()
            #return HttpResponse(data)
            
        else:
                print(f"Error fetching breath rate data for {date}: {breathrate_response.status_code}")
              
        spo2_url= f'https://api.fitbit.com/1/user/-/spo2/date/2021-10-04.json'
       
        spo2_response = requests.get(spo2_url, headers=headers)
        print('spO2 Value:')
        print(spo2_response.content)
        if spo2_response.status_code == 200:
            data = spo2_response.json()
            #return HttpResponse(data)
            
        else:
                print(f"Error fetching breath rate data for {date}: {spo2_response.status_code}")
                #return HttpResponse('Error fetching breath rate data ')
        activity_url= f'https://api.fitbit.com/1/user/-/activities/list.json'
        params = {
            'afterDate': '2019-01-01',
            'offset': 0,
            'limit': 10,
            'sort': 'asc'
        }
        activity_response = requests.get(activity_url, headers=headers,params=params)
        print('Activity Value :')
        print(activity_response.content)
        data = activity_response.json()
        activities = data['activities']

              # Extract and process each startTime
        start_times_str = [activity['startTime'] for activity in activities]
        start_times = []

        for start_time_str in start_times_str:
            # Parse the datetime string
            dt = datetime.strptime(start_time_str, "%Y-%m-%dT%H:%M:%S.%f%z")
            
            # Format the datetime without seconds and milliseconds
            formatted_start_time = dt.strftime("%Y-%m-%dT%H:%M")
            
            # Add the formatted start time to the list
            start_times.append(formatted_start_time)

        # Print the processed start times
        for start_time in start_times:
            print(start_time)
        zone_names = [zone['name'] for zone in data['activities'][0]['heartRateZones']]

                # Extract minutes data
        minutes_data = [[zone['minutes'] for zone in activity['heartRateZones']] for activity in data['activities']]
        print(minutes_data)
        # Number of activities
        num_activities = len(start_times)
        print(num_activities)
        # Width of each bar
        bar_width = 0.35

        # Plotting
        fig, ax = plt.subplots()

        # Define color map
        cmap = plt.get_cmap('tab10')
        i=0
        # Plot each bar and set color based on the value
        for i in range(num_activities):
            bars = ax.bar(i, minutes_data[i], bar_width, label=start_times[i])
            for j, bar in enumerate(bars):
                value = minutes_data[i][j]
                color = cmap(j % len(zone_names))
                bar.set_color(color)

        
        # Create a legend with zone names and their respective colors
        handles = [plt.Rectangle((0,0),1,1, color=cmap(i)) for i in range(len(zone_names))]
        ax.legend(handles, zone_names, loc='upper left', bbox_to_anchor=(1, 1))
 
        ax.set_ylabel('Minutes')
        ax.set_title('Minutes spent in Activity')
        ax.set_xlabel('StartTime')
        ax.set_xticks(np.arange(num_activities))
        ax.set_xticklabels(start_times, rotation=45, ha='right')  

        plt.tight_layout()
        plt.show()

        # Save the chart as an image
        image_path = 'all_activities.png'
        plt.savefig(image_path)
        heartrate_url = 'https://api.fitbit.com/1/user/-/activities/heart/date/today/1d.json'
        headers = {'Authorization': f'Bearer {access_token}'}
        heartrate_response = requests.get(heartrate_url, headers=headers)
        heart_rate_data = heartrate_response.json()
        print(heart_rate_data)
       
        # Extract dateTime and value
        for entry in heart_rate_data['activities-heart']:
            dateTime = entry['dateTime']
            value = entry['value']
            print("Date:", dateTime)
            print("Value:", value)
            heart_rate = HeartRate(
                value=value,
                dateTime=dateTime
            
            )
            heart_rate.save()    
        #heart_rate_data1 = heart_rate_data["activities-heart"][0]["value"]["heartRateZones"]
        return  HttpResponse("All  data saved successfully")    
    else:
            print(f"Error fetching breath rate data for {date}: {activity_response.status_code}")
            return HttpResponse('Error fetching breath rate data ')       

              
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
  