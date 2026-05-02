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
from django.utils import timezone
import random
from datetime import datetime, timedelta
import json
from dashboard.models import Order, MetricReading, SolarSensor, UtilityProvider
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.db.models.functions import TruncDay
from django.conf import settings
import requests

def dashboard_with_pivot(request):                                  #These are URLS for the django Dashboard!!
    return render(request, 'dashboard_with_pivot.html', {})         #
                                                                    #
def pivot_data(request):                                            #
    dataset = Order.objects.all()                                   #
    data = serializers.serialize('json', dataset)                   #
    return JsonResponse(data, safe=False)                           #

@csrf_exempt
def esp_ingest(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    voltage = payload.get("voltage")
    current = payload.get("current")
    power = payload.get("power")

    sensor_id = payload.get("sensor_id")
    sensor = None
    if sensor_id is not None:
        try:
            sensor = SolarSensor.objects.get(id=sensor_id)
        except SolarSensor.DoesNotExist:
            sensor = None

    if sensor is None:
        sensor = SolarSensor.objects.first()
    if sensor is None:
        return JsonResponse({"error": "No sensors configured"}, status=400)

    MetricReading.objects.create(
        user=sensor.user,
        sensor=sensor,
        timestamp=timezone.now(),
        source_ip=request.META.get("REMOTE_ADDR"),
        voltage=voltage,
        current=current,
        power=power,
        payload=payload,
    )

    return JsonResponse({"status": "ok", "received": True})

def esp_latest(request):
    sensor_id = request.GET.get("sensor_id")
    qs = MetricReading.objects.all()
    if sensor_id:
        qs = qs.filter(sensor_id=sensor_id)

    latest = qs.first()
    if latest is None:
        return JsonResponse({"last_seen": None, "payload": None, "connected": False})

    return JsonResponse({
        "last_seen": latest.timestamp.isoformat(),
        "payload": latest.payload,
        "connected": True,
    })


@login_required
def esp_sensors(request):
    sensors = list(
        SolarSensor.objects.filter(user=request.user)
        .order_by("id")
        .values("id", "name", "location", "sensor_type")
    )
    return JsonResponse({"sensors": sensors})


@login_required
def esp_series(request):
    sensor_id = request.GET.get("sensor_id")
    points_raw = request.GET.get("points", "200")

    try:
        points = int(points_raw)
    except ValueError:
        points = 200
    points = max(1, min(points, 2000))

    sensors_qs = SolarSensor.objects.filter(user=request.user).order_by("id")
    if not sensors_qs.exists():
        return JsonResponse({"sensor": None, "readings": []})

    if sensor_id is None:
        sensor = sensors_qs.first()
    else:
        sensor = get_object_or_404(sensors_qs, id=sensor_id)

    qs = (
        MetricReading.objects.filter(user=request.user, sensor=sensor)
        .order_by("-timestamp")
        .only("timestamp", "voltage", "current", "power")[:points]
    )

    readings = [
        {
            "timestamp": r.timestamp.isoformat(),
            "voltage": r.voltage,
            "current": r.current,
            "power": r.power,
        }
        for r in reversed(list(qs))
    ]

    return JsonResponse(
        {
            "sensor": {"id": sensor.id, "name": sensor.name},
            "readings": readings,
        }
    )


@login_required
def esp_net_power_daily(request):
    days_raw = request.GET.get("days", "7")
    try:
        days = int(days_raw)
    except ValueError:
        days = 7
    days = max(1, min(days, 31))

    now = timezone.now()
    start = now - timedelta(days=days)

    qs = (
        MetricReading.objects.filter(user=request.user, timestamp__gte=start)
        .exclude(power__isnull=True)
        .annotate(day=TruncDay("timestamp"))
        .values("day")
        .annotate(net_power_w=Avg("power"))
        .order_by("day")
    )

    data = [
        {
            "day": row["day"].date().isoformat() if row["day"] else None,
            "net_power_w": float(row["net_power_w"]) if row["net_power_w"] is not None else None,
        }
        for row in qs
    ]

    return JsonResponse({"days": data})


@login_required
def esp_net_energy_daily(request):
    days_raw = request.GET.get("days", "7")
    try:
        days = int(days_raw)
    except ValueError:
        days = 7
    days = max(1, min(days, 31))

    now = timezone.now()
    start = now - timedelta(days=days)

    sensor_ids = list(SolarSensor.objects.filter(user=request.user).values_list("id", flat=True))
    if not sensor_ids:
        return JsonResponse({"days": []})

    totals_wh = {}

    for sensor_id in sensor_ids:
        readings = list(
            MetricReading.objects.filter(
                user=request.user,
                sensor_id=sensor_id,
                timestamp__gte=start,
                power__isnull=False,
            )
            .order_by("timestamp")
            .values("timestamp", "power")
        )

        if len(readings) < 2:
            continue

        prev = readings[0]
        for cur in readings[1:]:
            t0 = prev["timestamp"]
            t1 = cur["timestamp"]
            if t0 is None or t1 is None:
                prev = cur
                continue

            dt_hours = (t1 - t0).total_seconds() / 3600.0
            if dt_hours <= 0:
                prev = cur
                continue

            p0 = float(prev["power"])
            p1 = float(cur["power"])
            e_wh = ((p0 + p1) / 2.0) * dt_hours

            day_key = t0.date().isoformat()
            totals_wh[day_key] = totals_wh.get(day_key, 0.0) + e_wh

            prev = cur

    days_sorted = sorted(totals_wh.keys())
    data = [{"day": day, "net_energy_wh": totals_wh[day]} for day in days_sorted]
    return JsonResponse({"days": data})


_UTILITY_CACHE = {}


UTILITY_STATES = [
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
]


@login_required
def utility_states(request):
    return JsonResponse({"states": UTILITY_STATES})


@login_required
def utility_rate(request):
    state = request.GET.get("state")
    utility_id = request.GET.get("utility_id")
    now = timezone.now()
    cache_key = f"utility:{utility_id}" if utility_id else (state or "default")

    cached = _UTILITY_CACHE.get(cache_key)
    if cached is not None:
        if (now - cached["ts"]).total_seconds() < 6 * 3600:
            return JsonResponse(cached["payload"])

    rate = float(getattr(settings, "UTILITY_KWH_RATE_USD", 0.15))
    source = "configured"

    if utility_id:
        try:
            utility = UtilityProvider.objects.get(id=utility_id)
        except UtilityProvider.DoesNotExist:
            utility = None

        if utility is None or utility.manual_rate_usd_per_kwh is None:
            out = {
                "utility": None,
                "rate_usd_per_kwh": rate,
                "source": source,
                "as_of": now.isoformat(),
            }
            _UTILITY_CACHE[cache_key] = {"ts": now, "payload": out}
            return JsonResponse(out)

        out = {
            "utility": {"id": utility.id, "name": utility.name, "rate_source_url": utility.rate_source_url},
            "rate_usd_per_kwh": float(utility.manual_rate_usd_per_kwh),
            "source": "custom",
            "as_of": now.isoformat(),
        }
        _UTILITY_CACHE[cache_key] = {"ts": now, "payload": out}
        return JsonResponse(out)

    api_key = getattr(settings, "UTILITY_EIA_API_KEY", None)
    if api_key and state:
        try:
            url = "https://api.eia.gov/v2/electricity/retail-sales/data/"
            params = {
                "api_key": api_key,
                "frequency": "monthly",
                "data[0]": "price",
                "facets[stateid][]": state,
                "facets[sectorid][]": "RES",
                "sort[0][column]": "period",
                "sort[0][direction]": "desc",
                "length": 1,
            }
            resp = requests.get(url, params=params, timeout=5)
            resp.raise_for_status()
            payload = resp.json()
            rows = payload.get("response", {}).get("data", [])
            if rows and rows[0].get("price") is not None:
                cents_per_kwh = float(rows[0]["price"])
                rate = cents_per_kwh / 100.0
                source = f"eia:{state}"
        except Exception:
            pass

    out = {
        "state": state,
        "rate_usd_per_kwh": rate,
        "source": source,
        "as_of": now.isoformat(),
    }
    _UTILITY_CACHE[cache_key] = {"ts": now, "payload": out}
    return JsonResponse(out)


@csrf_exempt
@login_required
def utility_custom(request):
    if request.method == "GET":
        rows = list(
            UtilityProvider.objects.filter(use_eia=False)
            .order_by("name")
            .values("id", "name", "manual_rate_usd_per_kwh", "rate_source_url")
        )
        return JsonResponse({"utilities": rows})

    if request.method != "POST":
        return JsonResponse({"error": "GET or POST only"}, status=405)

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    name = (payload.get("name") or "").strip()
    rate = payload.get("rate_usd_per_kwh")
    rate_source_url = (payload.get("rate_source_url") or "").strip()

    if not name:
        return JsonResponse({"error": "name is required"}, status=400)
    if rate is None:
        return JsonResponse({"error": "rate_usd_per_kwh is required"}, status=400)

    try:
        if isinstance(rate, str):
            rate = rate.strip().replace("$", "").replace(",", "")
        rate_f = float(rate)
    except Exception:
        return JsonResponse({"error": "rate_usd_per_kwh must be a number"}, status=400)

    if rate_f <= 0:
        return JsonResponse({"error": "rate_usd_per_kwh must be > 0"}, status=400)

    obj, _created = UtilityProvider.objects.update_or_create(
        name=name,
        defaults={
            "use_eia": False,
            "eia_state": "",
            "manual_rate_usd_per_kwh": rate_f,
            "rate_source_url": rate_source_url,
        },
    )

    return JsonResponse(
        {
            "status": "ok",
            "utility": {
                "id": obj.id,
                "name": obj.name,
                "manual_rate_usd_per_kwh": obj.manual_rate_usd_per_kwh,
                "rate_source_url": obj.rate_source_url,
            },
        }
    )





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
