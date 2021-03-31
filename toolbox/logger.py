import logging
import sys

from structlog import configure
from structlog._log_levels import add_log_level
from structlog.processors import JSONRenderer, TimeStamper
from structlog.stdlib import filter_by_level

from toolbox.config import Config


def logger_initial_config():
    def add_service(_1, _2, event_dict):
        """
        Add the service name to the event dict.
        """
        event_dict["service"] = Config.NAME
        return event_dict

    def add_log_severity(_1, method_name, event_dict):
        """
        Add the logging level to the event dict as 'severity'
        """
        if method_name == "warn":
            # The stdlib has an alias, we always want 'warning' in full
            method_name = "WARNING"

        if method_name == "exception":
            # exception level is not as universal, use 'error' instead
            method_name = "ERROR"

        event_dict["severity"] = method_name.upper()
        return event_dict

    logging.basicConfig(stream=sys.stdout, level=Config.LOG_LEVEL, format="%(message)s")

    configure(
        processors=[
            add_log_level,
            add_log_severity,
            filter_by_level,
            add_service,
            TimeStamper(fmt=Config.LOG_DATE_FORMAT, utc=True, key="created_at"),
            JSONRenderer(),
        ]
    )
    logging.getLogger('pika').setLevel(Config.LOG_LEVEL_PIKA)
