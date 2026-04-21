from django.utils import timezone

from dashboard.models import MetricReading, SolarSensor

from .simulated import fabricate_two_weeks


<<<<<<< HEAD
# ------------------------
# DATABASE CONNECTION
# ------------------------
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="admin124424$",
        database="solar_data"
    )
=======
def seed_two_weeks_for_sensor(sensor: SolarSensor) -> int:
    readings = fabricate_two_weeks(now=timezone.now().replace(tzinfo=None))
>>>>>>> e257ac7 (ummmmm idk what happened here. i think i updated the firmware to allow multiple sensor node ESP's to be flashed, and send readings to the main hub ESP.)

    objs = []
    for item in readings:
        ts = item["timestamp"]
        if timezone.is_naive(ts):
            ts = timezone.make_aware(ts, timezone.get_current_timezone())

        voltage = item.get("voltage")
        current = item.get("current")
        power = item.get("power")

        payload = {
            "sensor_id": sensor.id,
            "timestamp": ts.isoformat(),
            "voltage": voltage,
            "current": current,
            "power": power,
            "source": item.get("source"),
        }

        objs.append(
            MetricReading(
                user=sensor.user,
                sensor=sensor,
                timestamp=ts,
                source_ip=None,
                voltage=voltage,
                current=current,
                power=power,
                payload=payload,
            )
        )

    MetricReading.objects.bulk_create(objs)
    return len(objs)
