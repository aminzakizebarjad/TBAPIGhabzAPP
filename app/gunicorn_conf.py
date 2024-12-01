# Gunicorn config variables
loglevel = "info"
errorlog = "-"  # stderr
accesslog = "-"  # stdout
worker_tmp_dir = "/dev/shm"
graceful_timeout = 120
# maximize timeout because the graphs were not showing in low timeouts
timeout = 400
keepalive = 5
threads = 3