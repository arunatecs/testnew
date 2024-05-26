from django.contrib import admin
from fitbit_heartrate.models import FitbitIntegration,HeartRate
#from .models_mongo import HeartRate

admin.site.register(FitbitIntegration)
admin.site.register(HeartRate)