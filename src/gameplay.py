import os
import pickle
import string
import re
import random
from urllib import parse

from sklearn.model_selection import train_test_split

from collections import defaultdict
import numpy as np
import time
from IPython import display

from src.make_data import make_data

print('Loading game…')
if not (os.path.isdir('data')
        and os.path.exists('data/puzzles.pkl')
        and os.path.exists('data/vocab/pkl')
        and os.path.exists('data/freqs.pkl')):
    make_data()

print('Pre-show banter time…')
df = pickle.load(open('data/puzzles.pkl', 'rb'))

train_dates, test_dates = train_test_split(df.date.unique(), )

# train_puzzles = df.loc[df.date.isin(train_dates)]
test_puzzles = df.query('season > 25')

ngram_voc = pickle.load(open('data/vocab.pkl', 'rb'))
ngrams_count = pickle.load(open('data/freqs.pkl', 'rb'))

puzz_values = [
    #     '2500',
    '500',
    '600',
    '700',
    '600',
    '650',
    '500',
    '700',
    'Bankrupt',
    '600',
    '550',
    '500',
    '600',
    'Bankrupt',
    '650',
    '500',
    '700',
    'Lose A Turn',
    '800',
    '500',
    '650',
    '500',
    '900',
    #     'Bankrupt',
]
print('Game Loaded!')


def calc_ngram_freq(pattern, remaining, max_n=5, counts=ngrams_count, voc=ngram_voc):
    n = len(pattern)
#     print(pattern)
    locs = [i for i, letter in enumerate(pattern) if letter == '_']
    if len(locs) != 1:
        return {}
    missing = locs[0]
    if n > max_n:
        #         print('long')
        n_sum = defaultdict(float)
        slices = [pattern[i:i+max_n]
                  for i in range(n-max_n+1) if '_' in pattern[i:i+5]]
        for s in slices:
            slice_freqs = calc_ngram_freq(s, remaining)
            for key, value in slice_freqs.items():
                n_sum[key] += value
        return {k: v / len(slices) for k, v in n_sum.items()}

    known = set(range(n))
    known.discard(missing)
    total = 0
    n_grams = [(k, i) for k, i in voc.items() if len(k) == n]
    if n == 1:
        indices = [(ng, i) for ng, i in n_grams if ng in remaining]
    else:
        indices = [(ng[missing], i) for ng, i in n_grams
                   if [ng[j] for j in known] == [pattern[j] for j in known]
                   and ng[missing] in remaining]
    n_counts = {}
    for letter, i in indices:
        total += counts[i]
        n_counts[letter] = counts[i]
    n_freqs = {k: v / total for k, v in n_counts.items()}
    return n_freqs


def find_chunks(masked_str):
    padded_masked_str = ' ' + masked_str + ' '
    missing_locs = [i for i, letter in enumerate(
        padded_masked_str) if letter == '_']
    if not missing_locs:
        return None
    chunks = []

    def tokenize_part(text):
        parts = text.split(' ')
        if len(parts) > 1:
            if '_' in parts[0]:
                return parts[0] + ' '
            elif '_' in parts[-1]:
                return ' ' + parts[-1]
            else:
                return ' ' + [part for part in parts if '_' in part][0] + ' '
        else:
            return text

    lb = 0
    cache = 0
    for loc in missing_locs:
        if lb == cache:
            cache = loc+1
            continue
        chunks.append(tokenize_part(padded_masked_str[lb:loc]))
        lb = cache
        cache = loc+1
    chunks.append(tokenize_part(padded_masked_str[lb:]))
    return chunks


def make_guess(masked_text, remaining, max_n=5):
    remaining_cons = remaining - set('AEIOU')
    remaining_vowels = remaining - remaining_cons
    masked_str = ''.join(masked_text)
    chunks = find_chunks(masked_str)
    guess_cons = defaultdict(float)
    guess_vowels = defaultdict(float)
    for chunk in chunks:
        chunk_freq = calc_ngram_freq(chunk, remaining, max_n)
        for letter in remaining_cons:
            guess_cons[letter] += chunk_freq.get(letter, 0)
        for letter in remaining_vowels:
            guess_vowels[letter] += chunk_freq.get(letter, 0)

    if guess_cons:
        best_cons = max(guess_cons.items(), key=lambda k: k[1])
    else:
        best_cons = (random.choice(remaining_cons), 0)
    if guess_vowels:
        best_vowel = max(guess_vowels.items(), key=lambda k: k[1])
    else:
        best_vowel = (random.choice(remaining_vowels), -1)
    return best_cons, best_vowel


def update_puzzle(masked_list, under, guess, remaining):
    right = 0
    if (guess in under) and (guess in remaining):
        locs = [i for i, letter in enumerate(under) if letter == guess]
        for pos in locs:
            masked_list[pos] = guess
        print(f"There are {len(locs)} {guess}'s in the puzzle!")
        right = len(locs)

    else:
        print(f"Sorry, no {guess}.")
    remaining.discard(guess)
    return masked_list, right


def full_game(rounds=3, puzzle_df=test_puzzles):
    display.clear_output()
    rules = (
        f"Let's play {rounds} rounds!"
    )
    round_puzzles = puzzle_df.query('round=="Round"')
    bonus_puzzles = puzzle_df.query('round=="Bonus"')
    print(rules)
    name = input("Player name: ")
    level = input("Choose computer level 1-5: ")
    while level not in ['1', '2', '3', '4', '5']:
        level = input("Invalid: Choose computer level 1-5: ")
    level = int(level)
    overall_scores = {name: 0, 'Computer': 0}
    if np.random.choice([0, 1]):
        #         print("Computer goes first!")
        comp_first = True
    else:
        #         print(f"{name} goes first!")
        comp_first = False
    for i in range(rounds):
        if i == 0:
            top = 2500
        elif i == 1:
            top = 3500
        else:
            i == 5000
        print(f"{name} Total: {overall_scores[name]}")
        print(f"Computer Total: {overall_scores['Computer']}")
        if (i % 2 != comp_first):
            input(f"Computer first round {i+1}. Enter to advance ")
        else:
            input(f"{name} first round {i+1}. Enter to advance ")
        time.sleep(.1)
        display.clear_output()
        sample_row = round_puzzles.sample(1)
        winner, score = play_puzzle(sample_row.puzzle.iloc[0],
                                    sample_row.category.iloc[0],
                                    (i % 2 != comp_first),
                                    level,
                                    name,
                                    top
                                    )
        display.clear_output()
        if score < 2000:
            print('Minimum 2000 for winner!')
            time.sleep(2)
            score = 2000
        overall_scores[winner] += score

    print(f"{name} Total: {overall_scores[name]}")
    print(f"Computer Total: {overall_scores['Computer']}")
    if overall_scores[name] > overall_scores['Computer']:
        print('You win!')
        input('Enter to advance to bonus round!')
        sample_row = bonus_puzzles.sample(1)
        winnings = bonus_round(sample_row.puzzle.iloc[0],
                               sample_row.category.iloc[0])
        try:
            winnings = int(winnings)
            print(f"Total Winnings: {winnings + overall_scores[name]}")
        except:
            print(f"Total Winnings: {winnings} + {overall_scores[name]}")
    else:
        print("Too bad, computer wins.")
        take_home = max([2000, overall_scores[name]])
        print(f'You won ${take_home}')


def create_puzzle_img(masked_text, category):
    puzzle_img_loc_base = "https://www.thewordfinder.com/wof-puzzle-generator/puzzle-thumb.php?bg=1&"
    puzzle_params = "ln1={}&ln2={}&ln3={}&ln4={}&cat={}&"
    masked_str = (''.join(masked_text)).split()
    curr_line = 0
    line = 0
    lines = ['']
    l1, l2, l3, l4 = '', '', '', ''
    display_img = True

    for word in masked_str:
        if (curr_line > 0) and (curr_line + len(word) > 10):
            line += 1
            curr_line = 0
            lines.append('')
        lines[line] += f'{parse.quote(word)} '
        curr_line += len(word) + 1

    if len(lines) == 4:
        l1, l2, l3, l4 = lines
    elif len(lines) == 3:
        l1, l2, l3 = lines
    elif len(lines) == 2:
        l2, l3 = lines
    elif len(lines) == 1:
        l2 = lines
    else:
        display_img = False
    if display_img:
        img_url = puzzle_img_loc_base + \
            puzzle_params.format(l1, l2, l3, l4, category)
        display.display(display.Image(url=img_url))
    return display_img


def bonus_round(text, category):
    display.clear_output(wait=True)
    win = False
    bonus_prize = np.random.choice([
        'A New Car',
        35000,
        50000,
        'A European Vacation',
        100000
    ])
    masked_text = list(re.sub(r'[ABCDFGHIJKMOPQUVWXYZ]', '_', text))
    display_img = create_puzzle_img(masked_text, category)
    if not display_img:
        print(f"Puzzle: {''.join(masked_text)}")
        print(f'Category: {category}')
    print("Given: RSTLNE")
    s = ''
    print()
    print("Guess 3 consonants and a vowel.")
    for i in range(3):
        letter = input(f"Consonant {i+1}: ").upper()
        while (len(letter) > 1) or (letter in set('AEIOU')):
            letter = input(f"Invalid input. Consonant {i+1}: ").upper()
        s += letter
    vowel = input("Vowel: ").upper()
    while (len(vowel) > 1) or (vowel not in set('AEIOU')):
        letter = input(f"Invalid input. Vowel: ").upper()
    s += vowel

    for guess in s:
        locs = [i for i, letter in enumerate(text) if letter == guess]
        for pos in locs:
            masked_text[pos] = guess

    left = 3
    sol = ''
    display.clear_output(wait=True)
    display_img = create_puzzle_img(masked_text)
    if not display_img:
        print(f"Puzzle: {''.join(masked_text)}")
        print(f'Category: {category}')
    print("Given: RSTLNE")
    print(f'Guessed Letters: {s}')
    while sol != text and left > 0:

        sol = input(f"Try to solve! {left} tries left: ").upper()
        left -= 1
        if sol == text:
            win = True
    display.clear_output(wait=True)
    print(f"Puzzle: {text}")
    print(f'Category: {category}')
    print("Given: RSTLNE")
    print(f'Guessed Letters: {s}')
    print(f'Your Guess: {sol}')
    print()
    if win:
        print("CONGRATULATIONS!!!")
        print(f"You won {bonus_prize}")
        return bonus_prize
    else:
        print(f"Too bad! You could have won {bonus_prize}")
        return 0


def spin(masked_text,
         text,
         category,
         remaining,
         scores,
         name, turn, top):
    wheel = [top] + puzz_values
    spaces = np.random.choice(len(wheel)) + int(len(wheel) * 0.5)
    for i in range(spaces):
        display.clear_output(wait=True)
        time.sleep(.1)
        print_puzzle_info(masked_text, category, remaining, scores, name, turn)
        print(f'Value: {wheel[i % len(wheel)]}')
    space = wheel[i % len(wheel)]
    return space


def player_turn(masked_text,
                text,
                category,
                remaining,
                scores,
                name,
                top
                ):
    vowel = True
    win = False
    rd = 0
    print_puzzle_info(masked_text, category, remaining, scores, name, name)
    time.sleep(.5)
    allowable = ['S',
                 'SPIN',
                 'V',
                 'SOLVE']
    if scores[name] < 250:
        mode = input('(S)pin or Sol(V)e? ')
        while mode.upper() not in allowable:
            mode = input('Invalid choice: (S)pin or Sol(V)e? ')
    else:
        allowable += ['B', 'BUY A VOWEL']
        mode = input('(S)pin, (B)uy a vowel, or Sol(V)e? ')
        while mode.upper() not in allowable:
            mode = input('Invalid choice: (S)pin, (B)uy a vowel, or Sol(V)e? ')
    if (mode.upper() == 'V') or (mode.upper() == 'SOLVE'):
        sol = input('Solution: ')
        if sol.upper() == text:
            masked_text = list(text)
            win = True
            print(f'Correct! {name} wins!')
        else:
            rd += 1
            print("Sorry, incorrect.")
            print("Computer's Turn!")
        time.sleep(3)
        return masked_text, scores, win, rd
    elif (mode.upper() == 'S') or (mode.upper() == 'SPIN'):
        space = spin(masked_text,
                     text,
                     category,
                     remaining,
                     scores, name, name, top)
        if space == 'Bankrupt':
            rd += 1
            print('Bankrupt!')
            print("Computer's Turn!")
            time.sleep(3)
            scores[name] = 0
            return masked_text, scores, win, rd
        elif space == 'Lose A Turn':
            rd += 1
            print('Lose a Turn!')
            print("Computer's Turn!")
            time.sleep(3)
            return masked_text, scores, win, rd
        else:
            vowel = False
            val = int(space)
    time.sleep(0.1)
    masked_text, right = player_guess(masked_text, text, vowel, remaining)
    if (mode.upper() == 'S') or (mode.upper() == 'SPIN'):
        scores[name] += right*val
    else:
        scores[name] -= 250
    if masked_text == list(text):
        display.clear_output()
        print_puzzle_info(masked_text, category, remaining,
                          scores, name, name)
        print(f'{name} wins!')
        win = True
    if not right:
        rd += 1
        print("Computer's Turn!")
    time.sleep(3)

    return masked_text, scores, win, rd


def computer_turn(masked_text,
                  text,
                  category,
                  remaining,
                  scores,
                  name,
                  level,
                  top):
    rd = 0
    win = False
    print_puzzle_info(masked_text, category, remaining,
                      scores, name, 'Computer')
    best_cons, best_vowel = make_guess(masked_text, remaining, level)
    if (best_cons[1] >= best_vowel[1]) or (scores['Computer'] < 250):
        space = spin(masked_text,
                     text,
                     category,
                     remaining,
                     scores, name, 'Computer', top)
        guess = best_cons[0]
        if space == 'Bankrupt':
            rd += 1
            print('Bankrupt!')
            print(f"{name}'s Turn!")
            time.sleep(3)
            scores['Computer'] = 0
            return masked_text, scores, win, rd
        elif space == 'Lose A Turn':
            rd += 1
            print('Lose a Turn!')
            print(f"{name}'s Turn!")
            time.sleep(3)
            return masked_text, scores, win, rd
        else:
            val = int(space)
            print(f"Guess: {guess}")
            masked_text, right = update_puzzle(
                masked_text, text, guess, remaining)
            scores['Computer'] += val*right
    else:
        scores['Computer'] -= 250
        guess = best_vowel[0]
        print(f'Buy an {guess}')
        masked_text, right = update_puzzle(masked_text, text, guess, remaining)

    if masked_text == list(text):
        display.clear_output()
        print_puzzle_info(masked_text, category, remaining,
                          scores, name, 'Computer')
        print('Computer wins!')
        win = True
    if not right:
        rd += 1
        print(f"{name}'s Turn!")
    time.sleep(3)

    return masked_text, scores, win, rd


def play_puzzle(text,
                category=None,
                comp_first=None,
                level=None,
                name=None,
                top=2500):
    if name is None:
        name = input("Player name: ")
    if level is None:
        level = int(input("Choose computer level 1-5: "))
        while level not in range(1, 6):
            level = int(input("Invalid. Choose computer level 1-5: "))
    if comp_first is None:
        if np.random.choice([0, 1]):
            print("Computer goes first!")
            comp_first = True
        else:
            print(f"{name} goes first!")
            comp_first = False
    masked_text = list(re.sub(r'[A-Z]', '_', text))
    remaining = set(string.ascii_uppercase)
    rd = 0
    scores = {name: 0, 'Computer': 0}
    while masked_text != list(text):
        display.clear_output(wait=True)
        if (rd % 2 == 0) == comp_first:
            masked_text, scores, win, inc = computer_turn(masked_text,
                                                          text,
                                                          category,
                                                          remaining,
                                                          scores,
                                                          name,
                                                          level,
                                                          top)
            if win:
                winner = 'Computer'
        else:
            masked_text, scores, win, inc = player_turn(masked_text,
                                                        text,
                                                        category,
                                                        remaining,
                                                        scores,
                                                        name,
                                                        top)
            if win:
                winner = name
        rd += inc
    # display.clear_output()
    return winner, scores[winner]


def player_guess(masked_text, text, vowel, remaining):
    kind = "vowel" if vowel else "consonant"
    guess = input(f"Guess a {kind}: ").upper()
    vowels = set('AEIOU')
    while len(guess) > 1 or ((guess in vowels) != vowel):
        guess = input(f"Invalid input. Guess a {kind}: ").upper()
    return update_puzzle(masked_text, text, guess, remaining)


def print_puzzle_info(masked, category, remaining, scores, player, turn):
    display_img = create_puzzle_img(masked, category)
    print(f'{player} score: {scores[player]}')
    print(f'Computer score: {scores["Computer"]}')
    print()
    if not display_img:
        print(f"Puzzle: {''.join(masked)}")
        print(f'Category: {category}')
    cons = remaining - set('AEIOU')
    vowels = remaining - cons
    print(f"Remaining Consonants: {''.join(sorted(cons))}")
    print(f"Remaining Vowels: {''.join(sorted(vowels))}")
    print()
    print(f"Turn: {turn}")


def custom_puzzle():
    puzzle = input("Puzzle: ").upper()
    winner, score = play_puzzle(puzzle, category='custom')
    print(f'{winner} won {score}!')
