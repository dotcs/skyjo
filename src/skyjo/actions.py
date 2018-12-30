class ActionType:
    RESET_GAME = 'RESET_GAME'
    LOCK_DECK = 'LOCK_DECK'
    NEXT_PLAYER = 'NEXT_PLAYER'
    PLAY_GIVE = 'PLAY_GIVE'
    PLAY_TAKE = 'PLAY_TAKE'
    PLAY_REJECT = 'PLAY_REJECT'
    ADD_PLAYER = 'ADD_PLAYER'
    OPEN_GAME = 'OPEN_GAME'


class ActionCreator:

    @staticmethod
    def reset_game():
        return {'type': ActionType.RESET_GAME}

    @staticmethod
    def lock_deck(lock):
        return {'type': ActionType.LOCK_DECK, 'lock': lock}

    @staticmethod
    def next_player():
        return {'type': ActionType.NEXT_PLAYER}

    @staticmethod
    def play_give():
        return {'type': ActionType.PLAY_GIVE}

    @staticmethod
    def play_take(pos):
        return {'type': ActionType.PLAY_TAKE, 'pos': pos}

    @staticmethod
    def play_reject(pos):
        return {'type': ActionType.PLAY_REJECT, 'pos': pos}

    @staticmethod
    def add_player(name):
        return {'type': ActionType.ADD_PLAYER, 'name': name}

    @staticmethod
    def open_game():
        return {'type': ActionType.OPEN_GAME}
