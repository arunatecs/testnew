from django.urls import path
from .views import fitbit_authorize, fitbit_callback,ecg_list,ecg_chart,home,dashboard
urlpatterns = [
    path('fitbit/authorize/ecg', fitbit_authorize, name='fitbit_authorize'),
    path('fitbit/callback/ecg', fitbit_callback, name='fitbit_callback'),
    path('fitbit/ecglist', ecg_list, name='ecglist'),
    #path('', dashboard, name='dashboard'),
    path('home/', home, name='home'),
    path('ecg/', ecg_list, name='ecg_list'),
    path('ecg/<str:ecg_id>/chart/', ecg_chart, name='ecg_chart'),
]
