from org_monitor import CustomRequestCounter, RequestCounterConfig

def test_custom_request_counter_with_labels():
    counter = CustomRequestCounter(RequestCounterConfig(
        name="test_requests_total",
        description="Test requests",
        label_names=["method", "endpoint"]
    ))
    counter.inc(method="GET", endpoint="/test")
    counter.inc(method="GET", endpoint="/test")
    samples = list(counter.counter.collect())[0].samples
    value = [s.value for s in samples if s.labels == {"method": "GET", "endpoint": "/test"}][0]
    assert value == 2