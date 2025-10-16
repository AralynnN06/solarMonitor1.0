# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class SolarSystem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    capacity_kw = models.FloatField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class SolarReading(models.Model):
    system = models.ForeignKey(SolarSystem, on_delete=models.CASCADE, related_name='readings')
    timestamp = models.DateTimeField(auto_now_add=True)
    power_output_kw = models.FloatField()
    efficiency_percent = models.FloatField()
    temperature_c = models.FloatField()
    
    class Meta:
        ordering = ['-timestamp']

class WeatherData(models.Model):
    system = models.ForeignKey(SolarSystem, on_delete=models.CASCADE, related_name='weather')
    timestamp = models.DateTimeField(auto_now_add=True)
    temperature = models.FloatField()
    cloud_coverage_percent = models.FloatField()
    wind_speed_kmh = models.FloatField()
    humidity_percent = models.FloatField()
    uv_index = models.FloatField()
    
    class Meta:
        ordering = ['-timestamp']

class OptimizationInsight(models.Model):
    system = models.CharField(max_length=20)