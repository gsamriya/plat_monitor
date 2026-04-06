import prometheus_client
from pydantic import BaseModel

class CounterConfig(BaseModel):
    name: str
    description: str

class CustomCounter:
    def __init__(self, config: CounterConfig):
        self.counter = prometheus_client.Counter(config.name, config.description)

    def inc(self, n: int = 1):
        self.counter.inc(n)

class RequestCounterConfig(BaseModel):
    name: str
    description: str
    label_names: list = []

class CustomRequestCounter:
    def __init__(self, config: RequestCounterConfig):
        self.counter = prometheus_client.Counter(config.name, config.description, config.label_names)

    def inc(self, **labels):
        self.counter.labels(**labels).inc()