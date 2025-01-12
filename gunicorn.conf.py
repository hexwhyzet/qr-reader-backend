import multiprocessing

bind = ":8080"
workers = min(multiprocessing.cpu_count() * 2 + 1, 16)  # Don't start too many workers:
max_requests = 2048
max_requests_jitter = 256
preload_app = True
timeout = 600
accesslog = None
loglevel = "warning"
worker_class = "sync"
