# Create your models here.
from django.db import models
from django.contrib.auth.models import User

# class SolarSystem(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     name = models.CharField(max_length=200)
#     capacity_kw = models.FloatField()
#     latitude = models.FloatField()
#     longitude = models.FloatField()
#     created_at = models.DateTimeField(auto_now_add=True)
    
#     def __str__(self):
#         return self.name

# class SolarReading(models.Model):
#     system = models.ForeignKey(SolarSystem, on_delete=models.CASCADE, related_name='readings')
#     timestamp = models.DateTimeField(auto_now_add=True)
#     power_output_kw = models.FloatField()
#     efficiency_percent = models.FloatField()
#     temperature_c = models.FloatField()
    
#     class Meta:
#         ordering = ['-timestamp']

# class WeatherData(models.Model):
#     system = models.ForeignKey(SolarSystem, on_delete=models.CASCADE, related_name='weather')
#     timestamp = models.DateTimeField(auto_now_add=True)
#     temperature = models.FloatField()
#     cloud_coverage_percent = models.FloatField()
#     wind_speed_kmh = models.FloatField()
#     humidity_percent = models.FloatField()
#     uv_index = models.FloatField()
    
# class Meta:
#         ordering = ['-timestamp']

# class OptimizationInsight(models.Model):
#     system = models.CharField(max_length=20)


class Order(models.Model):
    product_category = models.CharField(max_length=20)
    payment_method = models.CharField(max_length=50)
    shipping_cost = models.CharField(max_length=50)
    unit_price = models.DecimalField(max_digits=5, decimal_places=2)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    has_seeded_data = models.BooleanField(default=False)


class SolarSensor(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="solar_sensors")
    name = models.CharField(max_length=120)
    location = models.CharField(max_length=120)
    sensor_type = models.CharField(max_length=40)

    class Meta:
        unique_together = ("user", "name")


class MetricReading(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="metric_readings")
    sensor = models.ForeignKey(SolarSensor, on_delete=models.CASCADE, related_name="readings")
    timestamp = models.DateTimeField(db_index=True)
    source_ip = models.GenericIPAddressField(null=True, blank=True)
    voltage = models.FloatField(null=True, blank=True)
    current = models.FloatField(null=True, blank=True)
    power = models.FloatField(null=True, blank=True)
    payload = models.JSONField(default=dict)

    class Meta:
        ordering = ["-timestamp"]
