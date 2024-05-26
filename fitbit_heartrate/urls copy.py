from django.urls import path
from .views import fitbit_authorize, fitbit_callback,heart_rate_chart

urlpatterns = [
    path('fitbit/authorize/', fitbit_authorize, name='fitbit_authorize'),
    path('fitbit/callback/', fitbit_callback, name='fitbit_callback'),
    path('heart-rate-chart/', heart_rate_chart, name='heart_rate_chart'),
]