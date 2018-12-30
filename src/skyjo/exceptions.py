class GameFinishException(Exception):
    """
    This error message is thrown when the game is over.
    """
    pass


class DeckLockedException(Exception):
    """
    This error message is thrown if the deck was locked when it was accessed.
    """
    pass
