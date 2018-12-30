#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import copy
import numpy as np
from skyjo.exceptions import GameFinishException, DeckLockedException
from skyjo.reducer import reducer, _create_initial_state, _generate_deck, _give_card, _drop_filled_rows
from skyjo.actions import ActionCreator


class TestReducer(object):

    def test_generate_deck(self):
        deck = _generate_deck()

        assert deck['_size'] == 150
        assert deck[-2] == 5
        assert deck[-1] == 10
        assert deck[0] == 15
        for i in range(1, 13):
            assert deck[i] == 10

    def test_give_card(self):
        deck = _generate_deck()
        original_deck = copy.copy(deck)
        card = _give_card(deck)
        assert deck['_size'] == 149
        assert deck[card] == original_deck[card] - 1

    def test_drop_filled_rows_failure(self):
        mask_a = np.array([[1,1,np.nan],[1,1,1],[1,np.nan,1]])
        a = np.array([[1,2,5],[2,4,5],[1,9,5]])
        b, mask_b = _drop_filled_rows(a, mask_a)
        np.testing.assert_array_equal(b * mask_b, np.array([[1,2,np.nan], [2,4,5], [1,np.nan,5]]))

    def test_drop_filled_rows_success(self):
        mask_a = np.array([[1,1,np.nan],[1,1,1],[1,np.nan,1]])
        a = np.array([[1,2,5],[1,4,5],[1,9,5]])
        b, mask_b = _drop_filled_rows(a, mask_a)
        np.testing.assert_array_equal(b * mask_b, np.array([[2,np.nan], [4,5], [np.nan,5]]))

    ###########
    # Actions #
    ###########

    def test_reset_game(self):
        state = _create_initial_state()
        action = ActionCreator.reset_game()
        state = reducer(state, action)

        assert state is not None

    def test_lock_deck(self):
        state = _create_initial_state()

        action = ActionCreator.lock_deck(True)
        state = reducer(state, action)
        assert state['deck_locked'] is True

        action = ActionCreator.lock_deck(False)
        state = reducer(state, action)
        assert state['deck_locked'] is False

    def test_next_player(self):
        state = { 
            **_create_initial_state(),
            'players': [None, None, None],  # fake some players
            'current_player_ix': 1
        }

        action = ActionCreator.next_player()
        state = reducer(state, action)
        assert state['current_player_ix'] == 2

        action = ActionCreator.next_player()
        state = reducer(state, action)
        assert state['current_player_ix'] == 0

    def test_next_player_finish(self):
        state = { 
            **_create_initial_state(),
            'players': [None, None, None],  # fake some players
            'current_player_ix': 1,
            'finish_player_ix': 2
        }

        action = ActionCreator.next_player()
        with pytest.raises(GameFinishException):
            reducer(state, action)

    def test_add_player(self):
        state = _create_initial_state()

        action = ActionCreator.add_player("Foobar")
        state = reducer(state, action)
        assert len(state['players']) == 1
        player0 = state['players'][0] 
        assert player0['cards'].shape == (3,4)
        assert np.nansum(player0['mask']) == 0
        assert player0['name'] == 'Foobar'
        assert state['deck']['_size'] == 150 - 12

    def test_play_give(self):
        state = _create_initial_state()

        action = ActionCreator.play_give()
        state = reducer(state, action)

        assert not np.isnan(state['play_card'])
        assert state['deck']['_size'] == 149
        assert state['deck_locked'] is True

    def test_play_give_lock(self):
        state = _create_initial_state()

        state['deck_locked'] = True

        action = ActionCreator.play_give()
        with pytest.raises(DeckLockedException):
            reducer(state, action)

    def test_play_take(self):
        state = _create_initial_state()
        action = ActionCreator.add_player('Foobar')
        state = reducer(state, action)

        state['play_card'] = 10
        state['current_player_ix'] = 0
        state['players'][0]['cards'] = np.ones((3,4))
        state['deck_locked'] = True  # not strictly necessary, but could be the case

        action = ActionCreator.play_take((0,0))
        state = reducer(state, action)

        assert state['play_card'] == 1
        assert state['players'][0]['cards'][0,0] == 10
        assert state['players'][0]['mask'][0,0] == 1
        assert np.nansum(state['players'][0]['mask']) == 1
        assert state['finish_player_ix'] is None
        assert state['deck_locked'] is False

    def test_play_take_finish(self):
        state = _create_initial_state()
        action = ActionCreator.add_player('Foobar')
        state = reducer(state, action)

        state['play_card'] = 10
        state['current_player_ix'] = 0
        state['players'][0]['cards'] = np.ones((3,4))
        state['players'][0]['mask'] = np.ones((3,4))
        state['players'][0]['mask'][0,0] = np.nan

        action = ActionCreator.play_take((0,0))
        state = reducer(state, action)

        assert state['finish_player_ix'] == 0

    def test_play_reject(self):
        state = _create_initial_state()
        action = ActionCreator.add_player('Foobar')
        state = reducer(state, action)

        state['play_card'] = 10
        state['current_player_ix'] = 0
        state['players'][0]['cards'] = np.ones((3,4))
        state['deck_locked'] = True  # not strictly necessary, but could be the case

        action = ActionCreator.play_reject((0,0))
        state = reducer(state, action)

        assert state['play_card'] == 10
        assert state['players'][0]['cards'][0,0] == 1
        assert state['players'][0]['mask'][0,0] == 1
        assert np.nansum(state['players'][0]['mask']) == 1
        assert state['finish_player_ix'] is None
        assert state['deck_locked'] is False

    def test_play_reject_finish(self):
        state = _create_initial_state()
        action = ActionCreator.add_player('Foobar')
        state = reducer(state, action)

        state['play_card'] = 10
        state['current_player_ix'] = 0
        state['players'][0]['cards'] = np.ones((3,4))
        state['players'][0]['mask'] = np.ones((3,4))
        state['players'][0]['mask'][0,0] = np.nan

        action = ActionCreator.play_reject((0,0))
        state = reducer(state, action)

        assert state['finish_player_ix'] == 0

    def test_open_game(self):
        state = _create_initial_state()
        action = ActionCreator.add_player('Foobar0')
        state = reducer(state, action)
        action = ActionCreator.add_player('Foobar1')
        state = reducer(state, action)

        action = ActionCreator.open_game()
        state = reducer(state, action)

        assert np.nansum(state['players'][0]['mask']) == 2
        assert np.nansum(state['players'][1]['mask']) == 2
        assert not np.isnan(state['initial_player_ix'])
        assert state['initial_player_ix'] == state['current_player_ix']
        assert state['play_card'] is not None
