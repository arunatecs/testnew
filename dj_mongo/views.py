from django.shortcuts import redirect, render
from fitbit_heartrate.models_mongo import HeartRate
#from ecg.models_mongo import Ecg

def dashboard(request):
    
    heartrate = HeartRate.objects.all()
    print(heartrate)
    #ecg = Ecg.objects.all()

    # Combine data into a single structure
    combined_data = {
        'heartrate': heartrate,
        #'ecg': ecg,
    }


    return render(request, 'dashboard1.html',combined_data)
  