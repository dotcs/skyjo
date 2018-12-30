import numpy as np
import copy
from skyjo.actions import ActionType
from skyjo.exceptions import GameFinishException, DeckLockedException


def _create_initial_state():
    return {
        'players': [],
        'deck': _generate_deck(),
        'play_card': None,
        'initial_player_ix': None,
        'finish_player_ix': None,
        'current_player_ix': None,
        'deck_locked': False,
    }


def _create_player(name, cards):
    return {
        'name': name,
        'cards': cards,
        'mask': np.ones((3, 4)) * np.nan
    }


def _generate_deck():
    def n(card):
        if card == -2:
            return 5
        if card == 0:
            return 15
        else:
            return 10
    deck = {}
    for c in range(-2, 13):
        deck[c] = n(c)
    deck['_size'] = 150
    return deck


def _give_card(deck):
    cards = list(deck.keys())[:15]
    p = np.array(list(deck.values())[:15]) / deck['_size']
    card = np.random.choice(cards, p=p)
    deck['_size'] -= 1
    deck[card] -= 1
    return card


def _reveal_card(mask, pos):
    row, col = pos
    mask[row, col] = 1


def _get_random_unrevealed_card_pos(mask, size=1):
    indices = np.argwhere(np.isnan(mask))
    ixs = np.random.choice(np.arange(len(indices)), size=size, replace=False)
    return (indices[ix] for ix in ixs)


def _player_maxscore_index(players):
    ix = 0
    max_score = -100
    for i, player in enumerate(players):
        score = np.nansum(player['cards'] * player['mask'])
        if score > max_score:
            max_score = score
            ix = i
    return ix


def _finish_check(state):
    # skip method if other player has already finished the game
    if state['finish_player_ix'] is not None:
        return state

    ix = state['current_player_ix']
    player = state['players'][ix]

    # Mark current user as initiator of last round if all cards
    # have been revealed.
    if np.nansum(player['mask']) == 12:
        state['finish_player_ix'] = ix
    
    return state


def _drop_filled_rows(cards, mask):
    masked_cards = cards * mask
    m = np.all(masked_cards == cards[0, :], axis=0)
    return cards[:, ~m], mask[:, ~m]


def reducer(state, action):
    if action['type'] == ActionType.RESET_GAME:
        return _create_initial_state()
    elif action['type'] == ActionType.LOCK_DECK:
        return {**state, 'deck_locked': action['lock']}
    elif action['type'] == ActionType.NEXT_PLAYER:
        ix = state['current_player_ix'] + 1
        if ix >= len(state['players']):
            ix = 0
        if state['finish_player_ix'] is not None and state['finish_player_ix'] == ix:
            raise GameFinishException()
        return {**state, 'current_player_ix': ix}
    elif action['type'] == ActionType.PLAY_GIVE:
        if state['deck_locked']:
            raise DeckLockedException()
        deck = copy.copy(state['deck'])
        card = _give_card(deck)
        return {**state, 'deck': deck, 'play_card': card, 'deck_locked': True}
    elif action['type'] == ActionType.PLAY_TAKE:
        row, col = action['pos']
        ix = state['current_player_ix']
        player = state['players'][ix]
        cards = copy.copy(player['cards'])
        mask = copy.copy(player['mask'])

        # update
        old_card = cards[row, col]
        cards[row, col] = state['play_card']
        mask[row, col] = 1

        players = [*state['players']]
        players[ix]['cards'] = cards
        players[ix]['mask'] = mask

        return _finish_check({
            **state,
            'play_card': old_card,
            'players': players,
            'deck_locked': False
        })
    elif action['type'] == ActionType.PLAY_REJECT:
        row, col = action['pos']
        ix = state['current_player_ix']
        player = state['players'][ix]

        mask = copy.copy(player['mask'])
        mask[row, col] = 1

        players = [*state['players']]
        players[ix]['mask'] = mask

        return _finish_check({
            **state,
            'players': players,
            'deck_locked': False
        })
    elif action['type'] == ActionType.ADD_PLAYER:
        name = action['name']
        players = [*state['players']]
        deck = copy.copy(state['deck'])
        cards = np.array([_give_card(deck) for _ in range(12)]).reshape((3, 4))
        player = _create_player(name, cards)
        players.append(player)
        return {**state, 'players': players, 'deck': deck}
    elif action['type'] == ActionType.OPEN_GAME:
        players = [*state['players']]
        for ix, player in enumerate(players):
            mask = copy.copy(player['mask'])
            positions = _get_random_unrevealed_card_pos(mask, size=2)
            for pos in positions:
                _reveal_card(mask, pos)
            player['mask'] = mask

        initial_player_ix = _player_maxscore_index(players)

        deck = copy.copy(state['deck'])
        card = _give_card(deck)

        return {
            **state,
            'deck': deck,
            'players': players,
            'initial_player_ix': initial_player_ix,
            'current_player_ix': initial_player_ix,
            'play_card': card
        }

    return state
