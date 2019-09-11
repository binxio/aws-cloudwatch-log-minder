import os
import logging

log = logging.getLogger('cwlog-minder')
log.setLevel(os.getenv("LOG_LEVEL", "INFO"))
console = logging.StreamHandler()
console.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
log.addHandler(console)
