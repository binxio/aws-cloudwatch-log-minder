import os
import logging

log = logging.getLogger()
log.setLevel(os.getenv("LOG_LEVEL", "INFO"))
