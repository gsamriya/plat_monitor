from org_monitor import ProcessGauge, ProcessGaugeConfig, ProcessErrorCounter, ProcessErrorCounterConfig

def test_process_gauge_and_error_counter():
    gauge = ProcessGauge(ProcessGaugeConfig(name="test_process_running", description="Test process running"))
    error_counter = ProcessErrorCounter(ProcessErrorCounterConfig(name="test_process_errors", description="Test errors"))
    gauge.start()
    gauge.end()
    error_counter.inc()
    samples_gauge = list(gauge.gauge.collect())[0].samples
    samples_error = list(error_counter.counter.collect())[0].samples
    assert any(s.value == 0 for s in samples_gauge)  # ended, so should be 0
    assert any(s.value == 1 for s in samples_error)