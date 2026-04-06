# org_monitor

A simple Python monitoring module for exposing custom metrics to Prometheus. Works with any Python project. Example below uses FastAPI, but you can use it with any framework.

---

## Features

- Define and increment custom counters in your Python code
- Expose metrics in Prometheus format
- Easy integration with any Python project

---

## Quick Start

### 1. Prerequisites

- [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/) (for running the monitoring stack)
- Create the Docker network if it doesn't exist:
  ```sh
  docker network create monitoring
  ```
### 2. Start the Monitoring Stack

Run the following command to start the monitoring stack using Docker Compose:

```sh
docker-compose up -d
```

This will start Prometheus and Grafana services in detached mode.
### 3. Using the org_monitor module in your Python code

Using the custom `CustomCounter`:

```python
from org_monitor import CustomCounter, CounterConfig

# Create a custom counter
my_counter = CustomCounter(CounterConfig(name="my_counter", description="A custom counter"))

# Increment the counter
my_counter.inc(5)
```

Using the custom `CustomRequestCounter` with labels:

```python
from org_monitor import CustomRequestCounter, RequestCounterConfig

# Create a custom request counter with labels
request_counter = CustomRequestCounter(
    RequestCounterConfig(
        name="http_requests_total",
        description="Total HTTP requests",
        label_names=["method", "endpoint"]
    )
)


# Increment the counter with label values
request_counter.inc(method="GET", endpoint="/flip-coins")
```

> **Note:**  
> The keys passed to `inc()` must match the `label_names` defined in the config.  
> This allows you to track metrics per HTTP method, endpoint, or any other label you define.

### Using the custom `CustomTimer` for Request Latency/Duration

You can use `CustomTimer` to track request latency or duration in your Python application.  
Below is an example usage, as implemented in the FastAPI coin toss API:

```python
from org_monitor import CustomTimer, TimerConfig
from time import time

# Create a custom timer (optionally with labels)
request_timer = CustomTimer(
    TimerConfig(
        name="http_request_duration_seconds",
        description="Duration of HTTP requests in seconds",
        label_names=["method", "endpoint"]
    )
)

@app.get("/flip-coins")
async def flip_coin(times=None):
    start = time()
    try:
        # ... your endpoint logic ...
        pass
    finally:
        duration = time() - start
        request_timer.observe(duration, method="GET", endpoint="/flip-coins")
```
### Using Process Start/End and Error Metrics

You can use the process metrics utilities to track when a process starts, ends, and when errors occur.  
Below is an example usage:

```python
from org_monitor import (
    ProcessGauge, ProcessGaugeConfig,
    ProcessErrorCounter, ProcessErrorCounterConfig
)

# Create a gauge for process running state
process_gauge = ProcessGauge(
    ProcessGaugeConfig(
        name="my_process_running",
        description="Indicates if my process is running (1) or not (0)"
    )
)

# Create a counter for process errors
process_error_counter = ProcessErrorCounter(
    ProcessErrorCounterConfig(
        name="my_process_errors_total",
        description="Total number of errors in my process"
    )
)

def run_process():
    try:
        process_gauge.start()
        # ... your process logic ...
    except Exception:
        process_error_counter.inc()
        raise
    finally:
        process_gauge.end()
```

This will expose:
- `my_process_running` (gauge: 1 when running, 0 when not)
- `my_process_errors_total` (counter: increments on error)

You can visualize these metrics in Prometheus and Grafana just like your other application metrics.

---

### Visualizing Request Latency/Duration in Prometheus & Grafana

You can use the following PromQL queries to visualize request latency/duration using your `CustomTimer` metric (e.g., `http_request_duration_seconds`):

**Average Request Duration (per endpoint):**
```promql
rate(http_request_duration_seconds_sum{endpoint="/flip-coins"}[1m])
/
rate(http_request_duration_seconds_count{endpoint="/flip-coins"}[1m])
```

**95th Percentile Request Duration (per endpoint):**
```promql
histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket{endpoint="/flip-coins"}[1m])) by (le))
```

**Count of Requests (per endpoint):**
```promql
sum(rate(http_request_duration_seconds_count{endpoint="/flip-coins"}[1m]))
```

Use these queries in Prometheus or Grafana dashboards to monitor and visualize your application's request latency.



## Monitoring Stack

- **Prometheus:** [http://localhost:9090](http://localhost:9090)  
  - Config: [prometheus.yml](prometheus.yml)
  - Scrapes `coin-api:5000/metrics` every 5s
- **Grafana:** [http://localhost:3000](http://localhost:3000)  
  - Default login: `admin` / `your_password`
  - Add Prometheus as data source (`http://prometheus:9090`)
  - Create dashboards for your custom metrics

---

## Development

- Main API example: [`server.py`](server.py)
- Monitoring utilities: [`src/org_monitor`](src/org_monitor)


Here’s a step-by-step **Markdown guide** for setting up your monitoring stack with Vagrant, Docker, Prometheus, Grafana, FastAPI, and Node Exporter:

---



## Vagrant VM set

- Create a folder for Vagrant and add the following `Vagrantfile`:

```ruby
Vagrant.configure("2") do |config|
  config.vm.box = "bento/ubuntu-22.04"
  config.vm.box_version = "202502.21.0"
  config.vm.network "public_network", bridge: "en0: Wi-Fi", use_dhcp_assigned_default_route: true
  config.vm.network "forwarded_port", guest: 8000, host: 8000
  config.vm.network "forwarded_port", guest: 9100, host: 9100

  config.vm.provider "virtualbox" do |vb|
    vb.name = "FastAPI_Docker_VM"
    vb.memory = 1024
    vb.cpus = 2
  end

  config.vm.synced_folder "/Users/njanagaraj/Desktop/plat-api", "/home/vagrant/plat-api", owner: "vagrant", group: "vagrant"

  config.vm.provision "shell", inline: <<-SHELL
    sudo apt-get update
    sudo apt-get install -y docker.io curl
    sudo usermod -aG docker vagrant
    sudo systemctl enable docker
    sudo systemctl start docker
    sleep 5
    cd /home/vagrant/plat-api
    sudo docker build -t plat-api-app .
    sudo docker rm -f plat-api-running || true
    sudo docker run -d --name plat-api-running -p 8000:8000 plat-api-app

    NODE_EXPORTER_VERSION="1.9.1"
    ARCH="linux-arm64"
    cd /home/vagrant
    curl -LO https://github.com/prometheus/node_exporter/releases/download/v${NODE_EXPORTER_VERSION}/node_exporter-${NODE_EXPORTER_VERSION}.${ARCH}.tar.gz
    tar xzf node_exporter-${NODE_EXPORTER_VERSION}.${ARCH}.tar.gz
    sudo mv node_exporter-${NODE_EXPORTER_VERSION}.${ARCH}/node_exporter /usr/local/bin/
    sudo chmod +x /usr/local/bin/node_exporter
    rm -rf node_exporter-${NODE_EXPORTER_VERSION}.${ARCH}*
    sudo useradd -rs /bin/false node_exporter || true
    sudo tee /etc/systemd/system/node_exporter.service > /dev/null <<EOF
[Unit]
Description=Prometheus Node Exporter
After=network.target

[Service]
User=node_exporter
ExecStart=/usr/local/bin/node_exporter

[Install]
WantedBy=multi-user.target
EOF
    sudo systemctl daemon-reload
    sudo systemctl enable node_exporter
    sudo systemctl start node_exporter
  SHELL
end
```

> **Note:** Replace plat-api with your actual plat-api path.

```
vagrant up

```
**Note:** The above command helps you to start the the Virtual machine and provision Dockerbased plat-api and node-exporter. No manual configuration required. 

---

## 4. Start the Monitoring Stack

```sh
cd plat-monitor/docker
./start.sh
```

- **Prometheus:** [http://localhost:9090](http://localhost:9090)
- **Grafana:** [http://localhost:3000](http://localhost:3000)  
  Default login: `admin` / `your_password`

---

## 5. Prometheus Configuration

- File: prometheus.yml
- Example scrape configs:
  ```yaml
  scrape_configs:
    - job_name: 'prometheus'
      static_configs:
        - targets: ['localhost:9090']
    - job_name: 'node-exporter'
      static_configs:
        - targets: ['host.docker.internal:9100']
    - job_name: 'org-api'
      metrics_path: /metrics
      scheme: http
      static_configs:
        - targets: ['host.docker.internal:8000']
      basic_auth:
        username: "admin"
        password: "secret"
  ```

---

## 6. Grafana Setup

1. Go to [http://localhost:3000/connections/datasources/new](http://localhost:3000/connections/datasources/new)
2. **Connection:**  
   Prometheus server URL: `http://prometheus:9090`
3. Click **Save and Test**
4. Go to [http://localhost:3000/dashboards](http://localhost:3000/dashboards)
5. **Import a dashboard**  
   - Click "Import dashboard"
   - Enter dashboard ID: `1860` (Node Exporter Full)
   - Click **Load**
   - Set Prometheus as the data source and click **Import**

---

## 7. Metrics Available for the demo

- **http_requests_total**: Counter with handler, status, and method.
- **http_request_size_bytes**: Summary of incoming request sizes.
- **http_response_size_bytes**: Summary of outgoing response sizes.
- **http_request_duration_seconds**: Histogram of request durations.
- **http_request_duration_highr_seconds**: High-resolution histogram.



  ## Kibana and Elasticsearch Access

Kibana and Elasticsearch are hosted at:

- [http://localhost:5601/](http://localhost:5601/)

**Login credentials:**
- **Username:** `elastic`
- **Password:** `7eTbmQkh`

---

---

