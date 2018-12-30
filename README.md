# skyjo


An implementation of the game Skyjo in Python.
Skyjo is a card game that has been published in 2015 by [Magilano](https://magilano.eu/?lang=en).

## Description

For details of how the game is played please refer to the game manual.


### Actions

All actions are described in the [actions](./src/skyjo/actions.py) file.
The following actions are available:

```
RESET_GAME: Resets the game and creates a fresh deck with 150 cards
ADD_PLAYER: Adds a player to the game and gives him 12 cards from the deck
OPEN_GAME: Opens the game by providing a play card and randomly opens two cards for each player
NEXT_PLAYER: Passes control to the next player
PLAY_GIVE: Draw a new card from the deck
PLAY_TAKE: Player takes the card and exchanges it with one of his own cards
PLAY_REJECT: Player rejects the play card and reveals one of his own cards
LOCK_DECK: Locks the deck, so that the current player cannot take another card from the deck
```


### Deck

A deck consists of 150 cards, with the following distribution:

```
-2:  5 cards
-1: 10 cards
 0: 15 cards
 1: 10 cards
 2: 10 cards
 3: 10 cards
 4: 10 cards
 5: 10 cards
 6: 10 cards
 7: 10 cards
 8: 10 cards
 9: 10 cards
10: 10 cards
11: 10 cards
12: 10 cards
```

### Sample game

The game is implemented by using the redux principle. Have a look at [the sample game](./src/skyjo/sample_game.py) to
see how it works.
