from org_monitor import metrics_response

def test_metrics_response():
    output = metrics_response()
    assert b"# HELP" in output