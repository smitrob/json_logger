import json
import logging
import os
import re
import sys
import time
from inspect import currentframe, getframeinfo, stack
from logging.handlers import TimedRotatingFileHandler
from os import path
from plpycommon.error import Error
# from logging import INFO,WARNING,CRITICAL,ERROR,Logger

LOG = 100
ERROR = logging.ERROR
WARNING = logging.WARNING
CRITICAL = logging.CRITICAL
SQL = 25
INFO = logging.INFO
DEBUG = logging.DEBUG
WARN = logging.WARN

class JSONFormatter(logging.Formatter):

    def format(self, record):
        string_formatted_time = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(record.created))
        obj = {}
        obj["message"] = record.msg
        obj["level"] = record.levelname
        obj["time"] = f"{string_formatted_time}.{record.msecs:3.0f}Z"
        obj["epoch_time"] = record.created
        obj["lineno"] = record.lineno
        obj["module"] = record.module
        obj["filename"] = record.filename
        # obj['lineno'] = record.lineno
        if hasattr(record, "custom_dict") and isinstance(record.custom_dict, dict):
            if record.custom_dict is not None:
                for key, value in record.custom_dict.items():
                    if key.lower() == 'password':
                        continue
                    obj[key] = value
        if hasattr(record, "sql") and isinstance(record.sql, str):
            if record.sql is not None:
                sql = ' '.join(record.sql.split())
                # sql = sql.replace('\t','')
                # sql = sql.replace('\n', '')
                obj['sql'] = sql
        if hasattr(record, "error"):
            if record.error is not None:
                if isinstance(record.error, TypeError):
                    obj['error'] = ';'.join(record.error.args)
                elif isinstance(record.error, dict):
                    obj['error_code'] = record.error['code']
                    obj['error_message'] = record.error['message']
                    obj['error_reason'] = record.error['reason']

                    # obj['errors'] = record.error
                elif record.error is None:
                    pass
                else:
                    obj['error'] = str(record.error)
            else:
                pass
        # if self.pretty:
        #     return json.dumps(obj, indent=4, sort_keys=True)
        # else:
        try:
            json_string = json.dumps(obj, sort_keys=True, indent=4)
        except Exception as e:
            pass

        return json_string

class PLLogger(logging.Logger):
    # log levels


    # add new log levels
    logging.addLevelName(LOG, 'LOG')
    logging.addLevelName(SQL, 'SQL')

    # handler = logging.StreamHandler(sys.stdout)
    # formatter = JSONFormatter()
    # handler.setFormatter(formatter)
    # logging.addHandler(handler)

    def __init__(self, name):
        LOG = 100
        SQL = 25
        super(PLLogger, self).__init__(name)
        handler = logging.StreamHandler(sys.stdout)
        formatter = JSONFormatter()
        handler.setFormatter(formatter)
        self.addHandler(handler)
        if path.exists('/tmp'):
            rotating_handler = TimedRotatingFileHandler(filename=f'/tmp/{__name__}.log', when="midnight",
                                                        backupCount=10)
            formatter = JSONFormatter()
            rotating_handler.setFormatter(formatter)
            self.addHandler(rotating_handler)
        self.propagate = True
        if "DEBUG" in os.environ and os.environ["DEBUG"] == "true":
            self.setLevel(DEBUG)
        else:
            self.setLevel(ERROR)
            #self.getLogger("boto3").setLevel(WARNING)
            #self.getLogger("botocore").setLevel(WARNING)
        if "LOGGER_LEVEL" in os.environ:
            logger_level = os.environ["LOGGER_LEVEL"]
        else:
            logger_level = ERROR
        if logger_level in locals():
            self.setLevel(logger_level)
        else:
            self.setLevel(ERROR)
        sys.excepthook = self.uncaught_exception_handler

    def custom_args(self, locals, kwargs):

        if 'extra' not in kwargs:
            kwargs['extra'] = {}
        if 'error' in locals:
            kwargs['extra']['error'] = locals['error']
        if 'sql' in locals:
            kwargs['extra']['sql'] = locals['sql']
        if 'custom_dict' in locals:
            kwargs['extra']['custom_dict'] = locals['custom_dict']

    def debug(self, msg, *args, custom_dict=None, sql=None, error=None, **kwargs):
        """
        Log a message with severity 'DEBUG' on the root logger. If the logger has
        no handlers, call basicConfig() to add a console handler with a pre-defined
        format.
        """
        self.custom_args(locals(), kwargs)
        if self.isEnabledFor(CRITICAL):
            self._log(CRITICAL, msg, args, **kwargs)

    def error(self, msg, *args, custom_dict=None, sql=None, error=None, **kwargs):
        """
        Log 'msg % args' with severity 'ERROR'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.error("Houston, we have a %s", "major problem", exc_info=1)
        """
        self.custom_args(locals(), kwargs)
        if self.isEnabledFor(ERROR):
            self._log(ERROR, msg, args, **kwargs)

    def info(self, msg, *args, custom_dict=None, sql=None, error=None, **kwargs):
        """
        Log 'msg % args' with severity 'INFO'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.info("Houston, we have a %s", "major problem", exc_info=1)
        """
        self.custom_args(locals(), kwargs)
        if self.isEnabledFor(INFO):
            self._log(INFO, msg, args, **kwargs)

    def warning(self, msg, *args, custom_dict=None, sql=None, error=None, **kwargs):
        """
        Log 'msg % args' with severity 'WARNING'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.warning("Houston, we have a %s", "major problem", exc_info=1)
        """
        self.custom_args(locals(), kwargs)
        if self.isEnabledFor(WARNING):
            self._log(WARNING, msg, args, **kwargs)

    def critical(self, msg, *args, custom_dict=None, sql=None, error=None, **kwargs):
        """
        Log 'msg % args' with severity 'CRITICAL'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.critical("Houston, we have a %s", "major problem", exc_info=1)
        """
        self.custom_args(locals(), kwargs)
        if self.isEnabledFor(CRITICAL):
            self._log(CRITICAL, msg, args, **kwargs)

    def sql(self, msg, *args, custom_dict=None, sql=None, error=None, **kwargs):
        """
        Log 'msg % args' with severity 'SQL'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.sql("Houston, we have a %s", "major problem", exc_info=1)
        """
        self.custom_args(locals(), kwargs)
        if self.isEnabledFor(SQL):
            self._log(SQL, msg, args, **kwargs)

    def log(self, msg, *args, custom_dict=None, sql=None, error=None, **kwargs):
        """
        Log 'msg % args' with the integer severity 'level'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.log(level, "We have a %s", "mysterious problem", exc_info=1)
        """
        self.custom_args(locals(), kwargs)
        if self.isEnabledFor(LOG):
            self._log(LOG, msg, args, **kwargs)

    def set_level(self, logger_level):
        self.setLevel(logger_level)

    def uncaught_exception_handler(self,exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        self.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


def getLogger(name=None, custom_logger=True):
    """
    Get a logger in the standard way, this will be a custom logger unless you specify otherwise.

    example:
        logger = json_logger.getLogger(__name__)

    :param name:
    :param custom_logger:
    :return:
    """
    if not custom_logger:
        return logging.getLogger(name)
    logging_class = logging.getLoggerClass()  # store the current logger factory for later
    logging._acquireLock()  # use the global logging lock for thread safety
    try:
        logging.setLoggerClass(PLLogger)  # temporarily change the logger factory
        logger = logging.getLogger(name)
        logging.setLoggerClass(logging_class)  # be nice, revert the logger factory change
        return logger
    finally:
        logging._releaseLock()

