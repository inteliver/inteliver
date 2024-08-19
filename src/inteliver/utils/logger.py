from loguru import logger

# commented to use the default loguru logger
# Remove default logger to add a custom one
# logger.remove()

# Add a logger that outputs to the console
# logger.add(sys.stdout, level="DEBUG", format="{level}: {time} {message}")

# Add a logger that outputs to a file with rotation and retention
logger.add(
    "logs/inteliver.log",
    level="DEBUG",
    rotation="10 MB",
    retention="10 days",
)

# Optional: Add more handlers as needed, for example, an error log file
logger.add(
    "logs/inteliver.error.log",
    level="ERROR",
    rotation="1 MB",
    retention="10 days",
)
