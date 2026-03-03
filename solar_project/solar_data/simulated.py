
from solar_data import insert_raw_with_timestamp

import math
from datetime import datetime, timedelta
import random

def fabricate_two_weeks():

    start_time = datetime.now() - timedelta(days=14)
    interval = timedelta(minutes=5)
    current_time = start_time

    while current_time <= datetime.now():

        hour = current_time.hour

        # Solar curve
        if 6 <= hour <= 18:
            solar_power = 500 * math.sin(math.pi * (hour - 6) / 12)
        else:
            solar_power = 0

        solar_voltage = 24
        solar_current = solar_power / solar_voltage if solar_voltage > 0 else 0

        load_power = random.uniform(200, 600)
        load_voltage = 120
        load_current = load_power / load_voltage

        insert_raw_with_timestamp(
            node_id=1,
            voltage=solar_voltage,
            current=solar_current,
            timestamp=current_time,
            source="simulated"
        )

        insert_raw_with_timestamp(
            node_id=4,
            voltage=load_voltage,
            current=load_current,
            timestamp=current_time,
            source="simulated"
        )

        current_time += interval


if __name__ == "__main__":
    fabricate_two_weeks()
    print("2 weeks of simulated data inserted.")