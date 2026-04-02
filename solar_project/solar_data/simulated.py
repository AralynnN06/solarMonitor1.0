
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

        # --- SOLAR PRODUCTION ---
        # Max 100W, active only between 6am and 6pm
        if 6 <= hour <= 18:
            solar_power = 100 * math.sin(math.pi * (hour - 6) / 12)
        else:
            solar_power = 0

        # --- LOAD (AC) ---
        # Random load between 0-300W regardless of time (battery covers nights)
        load_power = random.uniform(50, 300)
        load_voltage = 120.0
        load_current = load_power / load_voltage

        # --- BATTERY STATE ---
        # Battery charges when solar is producing, discharges when not
        # Voltage is slightly higher during charging, lower during discharging
        if solar_power > 0:
            battery_voltage = 13.6 + (solar_power / 100) * 1.0  # 13.6V to 14.6V while charging
        else:
            battery_voltage = random.uniform(12.5, 13.4)  # Discharging at night

        # --- DC NODE VOLTAGES (500mV drop at each node) ---
        v_node1 = 22.7                  # Solar Panel → MPPT
        v_node2 = v_node1 - 0.5        # MPPT → Battery (22.2V)
        v_node3 = battery_voltage       # Battery → Branch (reflects real battery state)

        # --- DC CURRENTS ---
        # During the day: solar power flows through nodes 1 and 2
        # At all times: battery supplies power to node 3 to cover the load
        # Convert AC load back to DC equivalent for battery current
        inverter_efficiency = 0.90
        dc_load_power = load_power / inverter_efficiency  # Power battery must supply (Equivalent in DC)

        i_node1 = solar_power / v_node1 if solar_power > 0 else 0
        i_node2 = solar_power / v_node2 if solar_power > 0 else 0
        i_node3 = dc_load_power / v_node3  # Battery always supplies load

        # --- INSERT ALL 4 NODES ---
        
        # Solar Panel to MPPT
        insert_raw_with_timestamp(
            node_id=1,
            voltage=v_node1,
            current=i_node1,
            timestamp=current_time,
            source="simulated"
        )

        # Node 2 — MPPT to Battery
        insert_raw_with_timestamp(
            node_id=2,
            voltage=v_node2,
            current=i_node2,
            timestamp=current_time,
            source="simulated"
        )

        # Node 3 — Battery to Branch
        insert_raw_with_timestamp(
            node_id=3,
            voltage=v_node3,
            current=i_node3,
            timestamp=current_time,
            source="simulated"
        )

        #Node 4 - Inverter to Load (AC)
        #Node (EUMs)
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