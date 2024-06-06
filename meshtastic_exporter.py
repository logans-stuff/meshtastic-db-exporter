import subprocess
import re
from prometheus_client import start_http_server, Gauge
import time
import argparse
import geohash2 as geohash

# Define the metrics
metrics = {
    'latitude': Gauge('meshtastic_node_latitude', 'Latitude of the node', ['user', 'id']),
    'longitude': Gauge('meshtastic_node_longitude', 'Longitude of the node', ['user', 'id']),
    'geohash': Gauge('meshtastic_node_geohash', 'Geohash of the node', ['geohash', 'user']),
    'altitude': Gauge('meshtastic_node_altitude', 'Altitude of the node', ['user', 'id']),
    'battery': Gauge('meshtastic_node_battery', 'Battery percentage of the node', ['user', 'id']),
    'channel_util': Gauge('meshtastic_node_channel_util', 'Channel utilization of the node', ['user', 'id']),
    'tx_air_util': Gauge('meshtastic_node_tx_air_util', 'Tx air utilization of the node', ['user', 'id']),
    'snr': Gauge('meshtastic_node_snr', 'Signal-to-noise ratio of the node', ['user', 'id']),
    'hops_away': Gauge('meshtastic_node_hops_away', 'Hops away of the node', ['user', 'id'])
}

# Function to run the meshtastic command and get the output
def get_meshtastic_nodes(device_ip):
    try:
        result = subprocess.run(['meshtastic', '--nodes', '--host', device_ip], capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running meshtastic command: {e}")
        return ""

# Function to parse the table
def parse_table(table_str, verbose):
    lines = table_str.strip().split('\n')
    
    header_index = None
    for i, line in enumerate(lines):
        if 'User' in line and 'Hardware' in line:
            header_index = i
            break
    
    if header_index is None:
        print("Error: Could not find the header line in the table.")
        return []

    header_line = lines[header_index]
    headers = [h.strip() for h in header_line.split('│')[1:-1]]

    nodes = []
    for line in lines[header_index + 2:]:
        if not line.strip() or line.startswith('╞') or line.startswith('├'):
            continue
        columns = line.split('│')[1:-1]
        if len(columns) != len(headers):
            if verbose:
                print(f"Skipping row with mismatched columns: {line}")
            continue
        node = {headers[i]: columns[i].strip() for i in range(len(headers))}
        nodes.append(node)
    
    return nodes

def update_metrics(nodes):
    for node in nodes:
        user = node.get('User', 'unknown')
        node_id = node.get('ID', 'unknown')
        
        latitude = node.get('Latitude', 'N/A')
        longitude = node.get('Longitude', 'N/A')
        
        if latitude != 'N/A' and longitude != 'N/A':
            latitude_value = float(latitude.replace('°', ''))
            longitude_value = float(longitude.replace('°', ''))
            geohash_value = geohash.encode(latitude_value, longitude_value)
        else:
            latitude_value = 0.0
            longitude_value = 0.0
            geohash_value = geohash.encode(0.0, 0.0)

        metrics['latitude'].labels(user=user, id=node_id).set(latitude_value)
        metrics['longitude'].labels(user=user, id=node_id).set(longitude_value)
        metrics['geohash'].labels(geohash=geohash_value, user=user).set(1)
        
        if 'Altitude' in node and node['Altitude'] != 'N/A':
            metrics['altitude'].labels(user=user, id=node_id).set(float(node['Altitude'].replace('m', '')))
        if 'Battery' in node and node['Battery'] != 'N/A':
            metrics['battery'].labels(user=user, id=node_id).set(float(node['Battery'].replace('%', '')))
        if 'Channel util.' in node and node['Channel util.'] != 'N/A':
            metrics['channel_util'].labels(user=user, id=node_id).set(float(node['Channel util.'].replace('%', '')))
        if 'Tx air util.' in node and node['Tx air util.'] != 'N/A':
            metrics['tx_air_util'].labels(user=user, id=node_id).set(float(node['Tx air util.'].replace('%', '')))
        if 'SNR' in node and node['SNR'] != 'N/A':
            metrics['snr'].labels(user=user, id=node_id).set(float(node['SNR'].replace(' dB', '')))
        if 'Hops Away' in node and node['Hops Away'] != 'N/A':
            hops_away = re.sub(r'/unknown', '', node['Hops Away'])
            metrics['hops_away'].labels(user=user, id=node_id).set(float(hops_away))

def main():
    parser = argparse.ArgumentParser(description='Meshtastic Prometheus Exporter')
    parser.add_argument('--host', required=True, help='IP address of the Meshtastic device')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    args = parser.parse_args()

    # Start the Prometheus HTTP server on port 8069
    start_http_server(8069)

    while True:
        table_str = get_meshtastic_nodes(args.host)
        if table_str:
            nodes = parse_table(table_str, args.verbose)
            update_metrics(nodes)
        time.sleep(45)  # Update every 45 seconds

if __name__ == '__main__':
    main()
