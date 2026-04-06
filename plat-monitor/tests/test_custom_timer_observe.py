from org_monitor import CustomTimer, TimerConfig

def test_custom_timer_observe():
    timer = CustomTimer(TimerConfig(
        name="test_timer_seconds",
        description="Test timer",
        label_names=["endpoint"]
    ))
    timer.observe(0.5, endpoint="/test")
    samples = list(timer.histogram.collect())[0].samples
    assert any(s.name == "test_timer_seconds_sum" for s in samples)
    assert any(s.name == "test_timer_seconds_count" for s in samples)