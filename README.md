# wheel

This repository contains a python implementation of [Wheel of Fortune](https://en.wikipedia.org/wiki/Wheel_of_Fortune_(U.S._game_show))

# Table of Contents

* Getting Started
* How to Play
* Data Download
* Computer Logic
* TODOs

# Getting Started

This repository was written in Python 3.6. Create an environment to be able to play using:
```
git clone git@github.com:lorenlchen/wheel.git
cd wheel
virtualenv wheelenv
. wheelenv/bin/activate
pip install -r requirements.txt
```
From there, launch a `jupyter notebook` (webapp hopefully forthcoming!) from the command line and open `play_wheel.ipynb`. Advance through the code cells to play a full game against the computer, or to play a custom puzzle!
# Gameplay
## Rules
Wheel of Fortune is a Hangman-variant, in which players attempt to reveal a hidden phrase by spinning a wheel and guessing letters. Each round begins with a puzzle composed of blank spaces representing letters. Punctuation and spaces are given. The first person to guess the solution to the puzzle wins the round.
### Taking a Turn
The active player has the option to spin, buy a vowel, or solve the puzzle. Control of the turn transfers to the next player if:
* An incorrect letter is guessed.
* An incorrect solve attempt is made.
* The wheel lands on "Bankrupt" or "Lose A Turn"

Otherwise, the active player retains control of the turn.
#### Spin
A player spins the wheel to determine a dollar value and guess a consonant. Guessing a correct consonant awards the player the dollar value from the wheel multiplied by the number of times the guessed letter appears in the puzzle. Guessing a correct letter also keeps the turn in the active player's control.

The wheel consists of 23 spaces and is composed mostly of dollar values ranging from 500-900, plus one "high-value" space, two "Bankrupt" spaces, one "Lose A Turn" space. The "high-value" space has a value of 2500 in round 1, 3500 in round 2, and 5000 beyond. Landing on "Lose A Turn" or "Bankrupt" automatically transfers control of the turn to the next player, while the latter also resets the player's current score for the round to 0.

#### Buy a Vowel
If the active player has a high enough current score for the round, they have the choice of buying a vowel (AEIOU). Buying a vowel costs the player $250, regardless of the number of occurences of the chosen vowel (even none). Guessing a correct vowel keeps the turn in the active player's control.

#### Solve
At any point, a player can elect to try to solve the puzzle, which involves guessing the full hidden text. If correct, the player wins the round and their current round score is added to their overall total. If incorrect, control is transferred to the next player.
(Note: in this implementation, solution attempts are case-insensitive, but still correct spelling, including punctuation is required to be judged a correct solve.)
## Full Game
`full_game(rounds)`: Follow prompts to play a specified number of rounds against the computer with AI level ranging from 1 (easiest) to 5 (hardest). Puzzles are randomly selected from real puzzles that aired from the last ten seasons of Wheel of Fortune.
If by the end of the game, the player's overall total is higher than the computer, the player will move on to the bonus round, where they will have a chance to win an extra prize.
### Bonus Round
The bonus round is a one player mini-game for the winner of the roundplay. It consists of a (usually short) puzzle with the letters RSTLNE automatically revealed. The player then has the opportunity to guess three more consonants and one additional vowel.  
In this implementation, after the revelation of these additional letters in the puzzle, the player will have three attempts to solve the puzzle no time limit). A successful attempt awards a hidden prize that is added to the previous total winnings.

## Custom Puzzle
`custom_puzzle`: This function gives the opportunity for a user to input a custom puzzle for another player to play in a single round against the computer. The puzzle writer should follow prompts to write the puzzle while the player is not looking, and then when finished, call the player to play the round as normal. During custom puzzles, the wheel is formatted as if it is round 1 (highest value of 2500).
# Data Download
Data for this application is scraped from [Wheel Compendium](http://buyavowel.boards.net/page/compendium), a fan-made archive of every Wheel of Fortune game in the Pat Sajak/Vanna White era.

To initialize the data download and computer logic creation, run:
```
python src/make_data.py
>> make_data()
```
Alternatively, attempting to play the game or importing `gameplay.py` without existing data will automatically try to initialize the objects.

# Computer AI

The computer's logic in guessing letters is governed by character n-gram frequency. Its knowledge base is the list of all puzzles that have been played in Wheel of Fortune history. The approximate logic is as follows:
1. Examine each hidden space remaining in the puzzle.
2. For each hidden space, consider the surrounding known letters, if any, and separate the puzzle into missing chunks. For example, the puzzle state:
`==PP=_=IRTH===` would be decomposed into: `['_=', '=PP', 'PP=_', '_=IRTH', 'IRTH=', '=', '=_']`
3. For each chunk, calculate the most likely of the remaining letters to be able to fill in the blank, based on frequency. Though `B` is not necessarily a common letter, it is almost surely filling in the blank in `_=IRTH`.