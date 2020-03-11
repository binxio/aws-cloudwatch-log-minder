import os
import logging

<<<<<<< HEAD
logging.basicConfig(
    format="%(levelname)s: %(message)s", level=os.getenv("LOG_LEVEL", "INFO")
)
=======
>>>>>>> 694e90a02027a76345d6a3e9cdb9712f90a08b29
log = logging.getLogger()
log.setLevel(os.getenv("LOG_LEVEL", "INFO"))
