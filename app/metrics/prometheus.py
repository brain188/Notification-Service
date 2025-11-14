# Prometheus instrumentation for observability.

from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Counter

# Custom counters
notification_sent = Counter("notification_sent_total", "Total notifications sent", ["channel"])
notification_failed = Counter("notification_failed_total", "Total failed notifications", ["channel"])

instrumentator = Instrumentator()