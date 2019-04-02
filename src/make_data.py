import os
import pickle

from bs4 import BeautifulSoup
import lxml
import requests
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split


def get_puzzles(
        curr_season=35,
        url_base='http://buyavowel.boards.net/page/compendium'):
    row_list = []
    for season in range(1, curr_season+1):
        url = f'{url_base}{season}'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'lxml')
        table = soup.find('div', {'id': 'zone_2'})
        rows = [row for row in table.find_all('tr')]
        for row in rows[1:]:
            items = row.find_all('td')
            if not items:
                continue
            if items[-1].text == 'BR':
                r = 'Bonus'
            else:
                r = 'Round'
            row_list.append([i.text.upper() for i in items[:-1]] + [r, season])
    return pd.DataFrame(row_list, columns=['puzzle', 'category', 'date', 'round', 'season'])


def make_data():
    # Reload Data
    print('Downloading puzzles…')
    df = get_puzzles()
    os.mkdir('data')
    df.to_pickle('data/puzzles.pkl')

    print('Initializing AI…')
    # unigrams = CountVectorizer(lowercase=False, analyzer='char', ngram_range=(1, 1))
    ngrams = CountVectorizer(lowercase=False, analyzer='char_wb', ngram_range=(1, 5))

    # X_u = unigrams.fit_transform(df.puzzle)
    X_n = ngrams.fit_transform(df.puzzle)

    # unigram_voc = unigrams.vocabulary_
    ngram_voc = ngrams.vocabulary_

    # unigrams_count = X_u.toarray().sum(axis=0)
    ngrams_count = X_n.toarray().sum(axis=0)

    pickle.dump(ngram_voc, open('data/vocab.pkl', 'wb'))
    pickle.dump(ngrams_count, open('data/freqs.pkl', 'wb'))
