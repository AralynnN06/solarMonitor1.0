from django.contrib.auth.signals import user_logged_in
from django.db import transaction
from django.dispatch import receiver

from solar_data.solar_data import seed_two_weeks_for_sensor

from .models import SolarSensor, UserProfile


@receiver(user_logged_in)
def seed_user_data_on_first_login(sender, request, user, **kwargs):
    profile, _ = UserProfile.objects.get_or_create(user=user)
    if profile.has_seeded_data:
        return

    with transaction.atomic():
        sensors = [
            ("Solar Panel → MPPT", {"location": "Roof", "sensor_type": "PV"}),
            ("MPPT → Battery", {"location": "Electrical", "sensor_type": "BAT"}),
            ("Battery → Inverter", {"location": "Electrical", "sensor_type": "INV"}),
        ]

        created = []
        for name, defaults in sensors:
            sensor, _ = SolarSensor.objects.get_or_create(
                user=user,
                name=name,
                defaults=defaults,
            )
            created.append(sensor)

        seed_two_weeks_for_sensor(created[1])
        profile.has_seeded_data = True
        profile.save(update_fields=["has_seeded_data"])
