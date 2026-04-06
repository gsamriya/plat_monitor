from org_monitor import CustomCounter, CounterConfig

def test_custom_counter_increment():
    counter = CustomCounter(CounterConfig(name="test_counter", description="Test counter"))
    counter.inc()
    counter.inc(2)
    samples = list(counter.counter.collect())[0].samples
    value = [s.value for s in samples if s.name == "test_counter_total"][0]
    assert value == 3