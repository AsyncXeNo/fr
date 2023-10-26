import sys

from loguru import logger

logger.remove()
logger.add(sys.stderr, format='<green>[{elapsed}]</green> <level>[{file}: {line}] > {message}</level>')
logger.add('logs/script.log', mode='w', format='[{elapsed}] [{file}: {line}] > {message}')