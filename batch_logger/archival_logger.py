import logging
import logging.config
import yaml

# Logging configuration from YAML
def setup_logging():
    # Load YAML configuration
    try:
        with open('config/logging_config.yaml', 'r') as file:
            config = yaml.safe_load(file)  # `safe_load` is compatible with Python 3.6
    except FileNotFoundError:
        print("Error: logging_config.yaml file not found.")
        exit(1)
    except yaml.YAMLError as e:
        print("Error: Failed to parse YAML configuration.")
        print(e)
        exit(1)

    # Apply the logging configuration
    try:
        logging.config.dictConfig(config)
    except Exception as e:
        print("Error: Failed to configure logging.")
        print(e)
        exit(1)

    # Test logging
    logger = logging.getLogger(__name__)
    # logger.debug("This is a debug message")
    logger.info("Logger is set")
    # logger.warning("This is a warning message")
    # logger.error("This is an error message")