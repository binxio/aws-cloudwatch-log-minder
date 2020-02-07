import os
import logging

logging.basicConfig(format="%(levelname)s: %(message)s", level=os.getenv("LOG_LEVEL", "INFO"))
log = logging.getLogger()
