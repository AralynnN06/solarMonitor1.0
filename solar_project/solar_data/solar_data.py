import mysql.connector
from datetime import datetime


# ------------------------
# DATABASE CONNECTION
# ------------------------
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="YOUR_PASSWORD",
        database="solar_data"
    )

# ------------------------
# INSERT RAW SENSOR DATA
# ------------------------
def insert_raw_reading(node_id, voltage, current, source="live"):

    power = voltage * current
    energy_wh = power * (1/60)  # assuming 1-minute interval

    connection = connect_db()
    cursor = connection.cursor()

    query = """
        INSERT INTO raw_readings
        (node_id, timestamp, voltage, current, power, energy_wh, data_source)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        node_id,
        datetime.now(),
        voltage,
        current,
        power,
        energy_wh,
        source
    )

    cursor.execute(query, values)
    connection.commit()
    cursor.close()
    connection.close()


def calculate_system_metrics():

    connection = connect_db()
    cursor = connection.cursor()

    # Total load power (example node IDs 4-7 = outlets)
    cursor.execute("""
        SELECT SUM(power)
        FROM raw_readings
        WHERE node_id BETWEEN 4 AND 7
        AND timestamp >= NOW() - INTERVAL 1 MINUTE
    """)
    total_load = cursor.fetchone()[0] or 0

    # Solar production (example node_id = 1)
    cursor.execute("""
        SELECT SUM(power)
        FROM raw_readings
        WHERE node_id = 1
        AND timestamp >= NOW() - INTERVAL 1 MINUTE
    """)
    solar_power = cursor.fetchone()[0] or 0

    # Net grid usage
    net_grid = total_load - solar_power

    # System efficiency
    efficiency = (solar_power / total_load * 100) if total_load > 0 else 0

    # Cost savings (assume $0.15 per kWh)
    cost_savings = (solar_power / 1000) * 0.15

    insert_metrics(total_load, solar_power, net_grid, efficiency, cost_savings)

    cursor.close()
    connection.close()


def insert_metrics(load, solar, grid, eff, savings):

    connection = connect_db()
    cursor = connection.cursor()

    query = """
        INSERT INTO system_metrics
        (timestamp, total_load_power, total_solar_power,
         net_grid_power, system_efficiency, estimated_cost_savings)
        VALUES (%s, %s, %s, %s, %s, %s)
    """

    values = (
        datetime.now(),
        load,
        solar,
        grid,
        eff,
        savings
    )

    cursor.execute(query, values)
    connection.commit()
    cursor.close()
    connection.close()

def calculate_roi(total_energy_kwh, system_cost):

    annual_savings = total_energy_kwh * 0.15
    roi_years = system_cost / annual_savings

    return roi_years

def insert_raw_with_timestamp(node_id, voltage, current, timestamp, source):

    power = voltage * current
    energy_wh = power * (5/60)  # 5-minute interval

    connection = connect_db()
    cursor = connection.cursor()

    query = """
        INSERT INTO raw_readings
        (node_id, timestamp, voltage, current, power, energy_wh, data_source)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        node_id,
        timestamp,
        voltage,
        current,
        power,
        energy_wh,
        source
    )

    cursor.execute(query, values)
    connection.commit()
    cursor.close()
    connection.close()