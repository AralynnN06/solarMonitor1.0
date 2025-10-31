from rest_framework import serializers
# from .models import SolarSystem, SolarReading, WeatherData

# class SolarReadingSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = SolarReading
#         fields = '__all__'

# class WeatherDataSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = WeatherData
#         fields = '__all__'

# class SolarSystemSerializer(serializers.ModelSerializer):
#     readings = SolarReadingSerializer(many=True, read_only=True)
#     weather = WeatherDataSerializer(many=True, read_only=True)
    
#     class Meta:
#         model = SolarSystem
#         fields = '__all__'