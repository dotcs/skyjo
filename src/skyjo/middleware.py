import logging
import json
from typing import Callable

from skyjo.NumpyEncoder import NumpyEncoder

logger = logging.getLogger('middleware')


def logger_middleware(dispatch: Callable, state_func: Callable):
    def next_func(next_handler):
        def action_func(action):
            # logger.info('PREV STATE: {}'.format(json.dumps(state_func(), cls=NumpyEncoder)))
            logger.info('ACTION: {}'.format(json.dumps(action, cls=NumpyEncoder)))
            val = next_handler(action)
            logger.info('NEW STATE: {}'.format(json.dumps(state_func(), cls=NumpyEncoder)))
            return val
        return action_func
    return next_func
