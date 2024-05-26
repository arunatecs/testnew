from django.urls import path
from .views import fitbit_authorize, fitbit_callback,breathrate_list
urlpatterns = [
    path('fitbit/authorize/', fitbit_authorize, name='fitbit_authorize'),
    path('fitbit/callback/', fitbit_callback, name='fitbit_callback'),
    
    path('breath/', breathrate_list, name='breathrate_list'),
    #path('breath/<str:ecg_id>/chart/', ecg_chart, name='ecg_chart'),
]
