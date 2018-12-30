import numpy as np
import logging
import asyncio
import aioredux

from skyjo.actions import ActionCreator, ActionType
from skyjo.exceptions import GameFinishException
from skyjo.reducer import reducer
from skyjo.middleware import logger_middleware
from skyjo.solver import simple_solver


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


def calculate_scores(players, finish_player_ix):
    scores = [np.sum(player['cards']) for player in players]
    if not np.argmin(scores) == finish_player_ix:
        scores[finish_player_ix] *= 2
    return scores


async def go():
    """
    Main routine.
    """
    initial_state = {}

    create_store_with_middleware = aioredux.apply_middleware(logger_middleware)(aioredux.create_store)
    store = await create_store_with_middleware(reducer, initial_state)

    await store.dispatch(ActionCreator.reset_game())
    await store.dispatch(ActionCreator.add_player("Foo"))
    await store.dispatch(ActionCreator.add_player("Bar"))
    await store.dispatch(ActionCreator.open_game())

    try:
        while True:
            state = store.state
            action = simple_solver(
                state['players'], state['current_player_ix'], state['play_card'], state['deck_locked'])
            await store.dispatch(action)

            # only go to next player if the play card has either been taken or rejected
            if action['type'] in (ActionType.PLAY_TAKE, ActionType.PLAY_REJECT):
                await store.dispatch(ActionCreator.next_player())

    except GameFinishException:
        state = store.state
        scores = calculate_scores(state['players'], state['finish_player_ix'])
        winner_ix = np.argmin(scores)
        print("Player #{} finished, Player #{} won. Scores: {}".format(
            state['finish_player_ix'],
            winner_ix,
            scores
        ))


if __name__ == "__main__":
    fix_np_seed()
    configure_logger()
    asyncio.get_event_loop().run_until_complete(go())
