# Create your views here.
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
# from .models import SolarSystem, SolarReading, WeatherData, OptimizationInsight
# from .serializers import SolarSystemSerializer, SolarReadingSerializer, WeatherDataSerializer
from .ai_analyzer import SolarOptimizer
import random
from datetime import datetime, timedelta
import json
from dashboard.models import Order
from django.core import serializers

latest_text = ""

def dashboard_with_pivot(request):                                  #These are URLS for the django Dashboard!!
    return render(request, 'dashboard_with_pivot.html', {})         #
                                                                    #
def pivot_data(request):                                            #
    dataset = Order.objects.all()                                   #
    data = serializers.serialize('json', dataset)                   #
    return JsonResponse(data, safe=False)                           #

def esp_data(request):
    global latest_text
    if request.method == "POST":
        data = json.loads(request.body)
        # Example: {"message": "Panel voltage is 12.3V"}
        latest_text = data.get("text", "")
        # Either save to DB or send to front end
        return JsonResponse({"status": "ok"})
    return JsonResponse({"error": "POST required"}, status = 400)

def dashboard(request):
    return render(request, "dashboard.html", {"latest_text": latest_text})

# def home(request):
#     return render(request, 'home.html')

# optimizer = SolarOptimizer()

# class SolarSystemViewSet(viewsets.ModelViewSet):
#     serializer_class = SolarSystemSerializer
    
#     def get_queryset(self):
#         return SolarSystem.objects.filter(user=self.request.user)
    
#     def perform_create(self, serializer):
#         serializer.save(user=self.request.user)
    
#     @action(detail=True, methods=['post'])
#     def add_reading(self, request, pk=None):
#         system = self.get_object()
#         reading = SolarReading.objects.create(
#             system=system,
#             power_output_kw=float(request.data.get('power_output_kw', 0)),
#             efficiency_percent=float(request.data.get('efficiency_percent', 85)),
#             temperature_c=float(request.data.get('temperature_c', 45))
#         )
#         return Response(SolarReadingSerializer(reading).data)
    
#     @action(detail=True, methods=['post'])
#     def add_weather(self, request, pk=None):
#         system = self.get_object()
#         weather = WeatherData.objects.create(
#             system=system,
#             temperature=float(request.data.get('temperature', 20)),
#             cloud_coverage_percent=float(request.data.get('cloud_coverage_percent', 30)),
#             wind_speed_kmh=float(request.data.get('wind_speed_kmh', 10)),
#             humidity_percent=float(request.data.get('humidity_percent', 60)),
#             uv_index=float(request.data.get('uv_index', 5))
#         )
#         return Response(WeatherDataSerializer(weather).data)
    
#     @action(detail=True, methods=['get'])
#     def analyze(self, request, pk=None):
#         system = self.get_object()
        
#         # Get recent data
#         readings = list(system.readings.all()[:30].values())
#         weather_data = list(system.weather.all()[:30].values())
        
#         if readings and weather_data:
#             solar_outputs = [r['power_output_kw'] for r in readings]
#             optimizer.train_model(
#                 optimizer.prepare_features(weather_data, readings),
#                 solar_outputs
#             )
        
#         # Predict optimal hours
#         optimization = optimizer.predict_optimal_hours(weather_data if weather_data else [{}] * 24)
#         recommendation = optimizer.generate_recommendation(optimization)
        
#         insight = OptimizationInsight.objects.create(
#             system=system,
#             optimal_usage_start=f"{optimization['start']:02d}:00",
#             optimal_usage_end=f"{optimization['end']:02d}:00",
#             predicted_output_kwh=optimization['predicted_output'],
#             recommendation=recommendation,
#             confidence_score=optimization['confidence']
#         )
        
#         return Response({
#             'optimal_start': optimization['start'],
#             'optimal_end': optimization['end'],
#             'predicted_output': optimization['predicted_output'],
#             'recommendation': recommendation,
#             'confidence': optimization['confidence']
#         })