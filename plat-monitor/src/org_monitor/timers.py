import prometheus_client
from pydantic import BaseModel

class TimerConfig(BaseModel):
    name: str
    description: str
    label_names: list = []

class CustomTimer:
    def __init__(self, config: TimerConfig):
        self.histogram = prometheus_client.Histogram(
            config.name, config.description, config.label_names
        )

    def observe(self, value, **labels):
        self.histogram.labels(**labels).observe(value)