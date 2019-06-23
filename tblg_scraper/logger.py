from logging import getLogger, DEBUG, INFO, Formatter, StreamHandler, handlers

logger = getLogger(__name__)
logger.setLevel(DEBUG)
formatter = Formatter('[%(asctime)s] [%(levelname)s] %(message)s')

# stdout
stdout_handler = StreamHandler()
stdout_handler.setLevel(INFO)
stdout_handler.setFormatter(formatter)
logger.addHandler(stdout_handler)

# file
file_handler = handlers.RotatingFileHandler(
    filename='log.txt',
    maxBytes=1048576,
    backupCount=3,
)
file_handler.setLevel(DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
