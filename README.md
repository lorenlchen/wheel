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
git clone path/to/wheel.git
cd wheel
virtualenv wheelenv
. wheelenv/bin/activate
pip install -r requirements.txt
```
From there, launch a jupyter notebook (webapp forthcoming!) from the command line with:
```
jupyter notebook
```
and open `play_wheel.ipynb`. Advance through the code cells to play a full game against the computer, or to play a custom puzzle!
# Data Download
Data for this application is scraped from [Wheel Compendium](insert link), a fanmade archive of every Wheel of Fortune game in the Pat Sajak/Vanna White era.

To initialize the data download and computer logic creation, run:
```
python make_data.py
>> make_data()
```
Alternatively, attempting to play the game without existing data will automatically try to initialize the objects.

# Gameplay
## Rules
Wheel of Fortune is a Hangman-variant, in which players attempt to reveal a hidden phrase by guessing letters.
### Taking a Turn
The active player has the option to spin, buy a vowel, or solve the puzzle. If the active player guesses an incorrect letter, makes an incorrect solve attempt, or spins a "Bankrupt" or "Lose A Turn",
### Spin
The player spins the wheel for the opportunity to call a consonant. The dollar value that the wheel lands on is the value of each correct consonant called. However, there are hazards spaces on the Wheel, Lose A Turn and Bankrupt, that automatically end your turn or reset your round score to 0 respectively.
## Full Game
Play a specified number of rounds against the computer, with AI levels from 1 (easiest) to 5 (hardest). Puzzles are randomly selected from real puzzles that aired from the last ten seasons of Wheel of Fortune. If by the end of the game, you have a higher score than the computer, you will move on to the bonus round, where you have a chance to win an extra prize.