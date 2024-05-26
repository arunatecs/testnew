# models.py
from django.db import models



class FitbitIntegration(models.Model):
    client_id = models.CharField(max_length=255)
    client_secret = models.CharField(max_length=255)
    redirect_uri = models.URLField()

     