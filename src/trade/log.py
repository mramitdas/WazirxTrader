import logging
import datetime
import os


def setup_logger():
    """
    Configures the logger with the desired settings.

    Args:
        None

    Returns:
        logging.Logger: The configured logger object.
    """
    try:
        os.mkdir("logs")
    except Exception:
        pass
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    log_file = f"logs/wazirX_{current_date}.log"
    logging.basicConfig(
        filename=log_file,
        filemode='a',
        format='%(asctime)s:%(msecs)d - %(levelname)s: %(message)s',
        datefmt='%d-%m-%y | %H:%M:%S',
        level=logging.DEBUG
    )

    return logging
