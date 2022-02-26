'''Настройки логирования.'''
from loguru import logger
from .paths import LOG_FOLDER

logger.add(f'{LOG_FOLDER}/info.log', filter=lambda record: record["level"].name == "INFO", retention='7 days')
logger.add(f'{LOG_FOLDER}/debug.log', filter=lambda record: record["level"].name == "DEBUG", retention='7 days')
logger.add(f'{LOG_FOLDER}/error.log', filter=lambda record: record["level"].name == "ERROR", retention='7 days', backtrace=True, diagnose=True)