import math
import random
from datetime import datetime, timedelta


def fabricate_two_weeks(now=None):
    if now is None:
        now = datetime.now()

    start_time = now - timedelta(days=14)
    interval = timedelta(minutes=5)
    current_time = start_time
    readings = []

    while current_time <= now:
        hour = current_time.hour

        if 6 <= hour <= 18:
            solar_power = 100 * math.sin(math.pi * (hour - 6) / 12)
        else:
            solar_power = 0.0

        load_power = random.uniform(50, 300)
        load_voltage = 120.0
        load_current = load_power / load_voltage

        inverter_efficiency = 0.90
        battery_power = load_power / inverter_efficiency

        if solar_power > 0:
            battery_voltage = 13.6 + (solar_power / 100.0)
        else:
            battery_voltage = random.uniform(12.5, 13.4)

        v_node1 = 22.7
        v_node2 = v_node1 - 0.5
        v_node3 = battery_voltage

        i_node1 = solar_power / v_node1 if solar_power > 0 else 0.0
        i_node2 = solar_power / v_node2 if solar_power > 0 else 0.0
        i_node3 = battery_power / v_node3

        readings.append(
            {
                "timestamp": current_time,
                "voltage": v_node1,
                "current": i_node1,
                "power": v_node1 * i_node1,
                "source": "simulated",
            }
        )
        readings.append(
            {
                "timestamp": current_time,
                "voltage": v_node2,
                "current": i_node2,
                "power": v_node2 * i_node2,
                "source": "simulated",
            }
        )
        readings.append(
            {
                "timestamp": current_time,
                "voltage": v_node3,
                "current": i_node3,
                "power": v_node3 * i_node3,
                "source": "simulated",
            }
        )
        readings.append(
            {
                "timestamp": current_time,
                "voltage": load_voltage,
                "current": load_current,
                "power": load_power,
                "source": "simulated",
            }
        )

        current_time += interval

    return readings


if __name__ == "__main__":
    data = fabricate_two_weeks()
    print(f"Generated {len(data)} simulated readings.")
