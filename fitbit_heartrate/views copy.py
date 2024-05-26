from django.shortcuts import redirect,render
import requests
from django.http import HttpResponseBadRequest
from fitbit_heartrate.models import FitbitIntegration,HeartRate
from django.http import JsonResponse
import json

fitbit_integration = FitbitIntegration.objects.last()
FITBIT_CLIENT_ID = fitbit_integration.client_id
FITBIT_CLIENT_SECRET = fitbit_integration.client_secret
FITBIT_REDIRECT_URI = fitbit_integration.redirect_uri

def fitbit_authorize(request):
    #print(FITBIT_REDIRECT_URI)
    # Redirect user to Fitbit for authorization
    auth_url = f'https://www.fitbit.com/oauth2/authorize?client_id={FITBIT_CLIENT_ID}&response_type=code&scope=activity%20heartrate%20location%20nutrition%20oxygen_saturation%20profile%20respiratory_rate%20settings%20sleep%20social%20temperature%20weight&code_challenge=0z0P__in0XUbu2HHKmn6YcsFVWeI2QgKDwKTisi-FBc&code_challenge_method=S256'
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

    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data['access_token']
        print(f'access_token:{access_token}')
        
       
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
        heart_rate_data1 = heart_rate_data["activities-heart"][0]["value"]["heartRateZones"]
    
        # Prepare data for the chart
        zone_names = [zone["name"] for zone in heart_rate_data1]
        minutes = [zone["minutes"] for zone in heart_rate_data1]
        heart_rates = [zone["max"] for zone in heart_rate_data1] 
        min_bpm = [zone["min"] for zone in heart_rate_data1]
        max_bpm = [zone["max"] for zone in heart_rate_data1] # Assuming max heart rate for each zone

        # Pass data to the template
        context = {
            'zone_names': json.dumps(zone_names),
            'minutes': json.dumps(minutes),
            'heart_rates': json.dumps(heart_rates),
            'min_bpm': json.dumps(min_bpm),
            'max_bpm': json.dumps(max_bpm),
        }
        print(context)

        return render(request, 'heart_rate_chart.html', context)     
        #return JsonResponse(heart_rate_data)
        """
        print('hai')
        ecg_url = 'https://api.fitbit.com/1/user/-/ecg/list.json'
        
        headers = {'Authorization': f'Bearer {access_token}'}
        ecg_response = requests.get(ecg_url, headers=headers)
        
        #ecg_data = ecg_response.json()
        print("hello")
        print(ecg_response)
        """ 
    else:
        return HttpResponseBadRequest("Failed to obtain access token from Fitbit")

def heart_rate_chart(request):
    # Sample heart rate data
    heart_rate_response = {
        "activities-heart": [
            {
                "dateTime": "2024-03-19",
                "value": {
                    "customHeartRateZones": [],
                    "heartRateZones": [
                        {"caloriesOut": 1281.339, "max": 109, "min": 30, "minutes": 1440, "name": "Out of Range"},
                        {"caloriesOut": 0, "max": 128, "min": 109, "minutes": 0, "name": "Fat Burn"},
                        {"caloriesOut": 0, "max": 151, "min": 128, "minutes": 0, "name": "Cardio"},
                        {"caloriesOut": 0, "max": 220, "min": 151, "minutes": 0, "name": "Peak"}
                    ],
                    "restingHeartRate": 73 
                }
            }
        ]
    }
    print(heart_rate_response)
    heart_rate_data = heart_rate_response["activities-heart"][0]["value"]["heartRateZones"]
    
    # Prepare data for the chart
    zone_names = [zone["name"] for zone in heart_rate_data]
    minutes = [zone["minutes"] for zone in heart_rate_data]
  
    context = {
        'zone_names': json.dumps(zone_names),
        'minutes': json.dumps(minutes),
    }
    print(context)

    return render(request, 'heart_rate_chart.html', context) 