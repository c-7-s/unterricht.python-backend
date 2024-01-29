import multiprocessing

max_requests = 1000
max_requests_jitter = 50
timeout = 120
log_file = "-"
workers = multiprocessing.cpu_count() * 2 + 1
bind = '0.0.0.0:8811'
worker_class = 'gevent'
loglevel = 'debug'
acceslogformat ="%(h)s %(l)s %(u)s %(t)s %(r)s %(s)s %(b)s %(f)s %(a)s"