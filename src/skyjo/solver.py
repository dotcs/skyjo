import numpy as np
from skyjo.actions import ActionCreator


def simple_solver(players, current_player_ix, play_card, deck_locked):
    """
    Simple solver that is based on a heuristic and is mainly used for demonstration purposes.
    """
    player = players[current_player_ix]
    cards = player['cards'] * player['mask']
    total = np.nansum(cards)
    other_players = [players[ix] for ix in range(len(players)) if ix != current_player_ix]
    other_players_totals = np.array([np.nansum(p['cards'] * p['mask']) for p in other_players])

    ixs_larger = np.argwhere(cards > play_card)
    ixs_equal = np.argwhere(cards == play_card)
    ixs_nan = np.argwhere(np.isnan(cards))

    if play_card > 4 and not deck_locked:
        return ActionCreator.play_give()
    if len(ixs_larger) > 0:
        cix = np.random.choice(range(len(ixs_larger)))
        return ActionCreator.play_take(ixs_larger[cix])
    if len(ixs_equal) > 0:
        if np.random.rand() > .5:
            cix = np.random.choice(range(len(ixs_equal)))
            return ActionCreator.play_take(ixs_equal[cix])
        else:
            cix = np.random.choice(range(len(ixs_nan)))
            return ActionCreator.play_reject(ixs_nan[cix])
    if len(ixs_nan) > 1:
        cix = np.random.choice(range(len(ixs_nan)))
        return ActionCreator.play_reject(ixs_nan[cix])
    if len(ixs_nan) == 1 and np.all(other_players_totals + 4 < total + play_card):
        return ActionCreator.play_take(ixs_nan[0])

    raise RuntimeError("No action available.")
