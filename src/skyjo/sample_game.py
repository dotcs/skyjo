import numpy as np
import logging
import asyncio
import aioredux

import skyjo.actions as actions
from skyjo.reducer import reducer
from skyjo.middleware import logger_middleware


def fix_np_seed():
    """
    By fixing the numpy random seed, all random actions are reproducible.
    """
    np.random.seed(0)


def configure_logger():
    """
    Configures the middleware logger.
    By default the logger writes all actions and resulting states into a file named 'game.log'.
    """
    logger = logging.getLogger('middleware')
    logger.setLevel(logging.DEBUG)

    fh = logging.FileHandler('game.log', mode="w")
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)

    logger.addHandler(fh)


async def go():
    """
    Main routine.
    """
    initial_state = {}

    create_store_with_middleware = aioredux.apply_middleware(logger_middleware)(aioredux.create_store)
    store = await create_store_with_middleware(reducer, initial_state)

    await store.dispatch(actions.reset_game())
    await store.dispatch(actions.add_player("Foo"))
    await store.dispatch(actions.add_player("Bar"))
    await store.dispatch(actions.open_game())
    await store.dispatch(actions.play_give())
    await store.dispatch(actions.play_take((2, 0)))
    await store.dispatch(actions.next_player())


if __name__ == "__main__":
    fix_np_seed()
    configure_logger()
    asyncio.get_event_loop().run_until_complete(go())
