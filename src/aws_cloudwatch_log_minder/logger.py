import os
import logging

log = logging.getLogger('cwlog-minder')
log.setLevel(os.getenv("LOG_LEVEL", "INFO"))
