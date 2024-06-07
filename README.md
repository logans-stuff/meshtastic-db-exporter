# Meshtastic NodeDB Exporter 
This small project assisted by chatgpt uses a Python script to host a Prometheus endpoint that can then be used within Grafana for visualization. This uses meshtastic's cli program to query the node for its node list and then parses this information without querying the mesh network or mqtt. 

## Instructions

### Step 1: Clone project
```sh
git clone https://github.com/logans-stuff/meshtastic-db-exporter.git
cd meshtastic-db-exporter
```
### Step 2: Modify docker-compose.yaml
Update the `docker-compose.yaml` file to include your node IP under the `HOST` environment variable for the` meshtastic_exporter` service.

### Step 3: Modify prometheus.yml
Update your Prometheus configuration file to include the Meshtastic Exporter. If you are using the provided `docker-compose.yaml`, create or modify the directory `/opt/adv-map/prometheus` and create or update the `prometheus.yml` file in that directory:

`/opt/adv-map/prometheus/prometheus.yml:`
```yaml
global:
  scrape_interval: 1m

scrape_configs:
  - job_name: 'prometheus'
    scrape_interval: 1m
    static_configs:
      - targets: ['0.0.0.0:9090']

  - job_name: 'meshtastic_exporter'
    scrape_interval: 1m
    static_configs:
      - targets: ['meshtastic_exporter:8069']
```

#### To Create required directories
If not already present, create the directory /opt/adv-map/ and change its ownership to your user:
```sh
sudo mkdir -p /opt/adv-map
sudo mkdir -p /opt/adv-map/prometheus
sudo chown -R $USER:$USER /opt/adv-map/
```

### Step 4: Build and run the Docker containers
Use docker-compose to build and run the containers:
```sh
docker-compose up --build -d
```

### Step 5: Access Prometheus and Grafana

Prometheus: `http://device_ip:9090`

Grafana: `http://device_ip:3000 `

#### Login to Grafana with the default credentials:

Username: `admin`

Password: `admin`

### Step 6: Add the basic dashboard or create your own
Dashboards > New > Import Dashboard > Paste JSON into box from meshtastic_dashboard.json

## Finished product:
![image](https://github.com/logans-stuff/meshtastic-db-exporter/assets/39987450/332e93ad-4c8a-4733-be8c-81d315eaed0b)

