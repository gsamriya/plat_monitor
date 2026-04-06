import prometheus_client
from pydantic import BaseModel

class ProcessGaugeConfig(BaseModel):
    name: str
    description: str

class ProcessErrorCounterConfig(BaseModel):
    name: str
    description: str

class ProcessGauge:
    def __init__(self, config: ProcessGaugeConfig):
        self.gauge = prometheus_client.Gauge(config.name, config.description)

    def start(self):
        self.gauge.set(1)

    def end(self):
        self.gauge.set(0)

class ProcessErrorCounter:
    def __init__(self, config: ProcessErrorCounterConfig):
        self.counter = prometheus_client.Counter(config.name, config.description)

    def inc(self):
        self.counter.inc()