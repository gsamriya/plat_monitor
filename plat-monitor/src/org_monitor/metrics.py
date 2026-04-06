import prometheus_client

def metrics_response():
    return prometheus_client.generate_latest()