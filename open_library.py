import requests
import json
import unittest
import os
import re
import sqlite3

from imdb import IMDb

def get_movie_titles_from_books(num_pages):
    ia = IMDb()
    movie_titles = []
    for page_number in range(num_pages):
        search_results = ia.get_keyword('based-on-novel', page=page_number+1)
        for movie in search_results:
            title = re.search(r'^([^()]+)', str(movie)).group(1)
            movie_titles.append(title.strip())
    return movie_titles

def get_title(movie_titles):
    book_list = []
    for movie_title in movie_titles:
        title = movie_title.split()
        title = title.join("+")
        book_list.append(title)
    return book_list
    
def get_book_ratings(book_list):
    rating_list = []
    for title in book_list:
        url = "https://openlibrary.org/search.json?title={title}"
        response = requests.get(url)
        if response.status_code == 200:
            book_data = json.loads(response.text)
            if book_data['Response'] == 'True':
                title = book_data['docs'][0]['2']['Title']
                rating = book_data['docs'][0]['0']['ratings_average']
                rating_list.append(title, rating)
    return rating_list


def create_database():
    conn = sqlite3.connect('ratings.db')
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS 'Open Library Ratings'
                 (title_id INTEGER PRIMARY KEY AUTOINCREMENT, rating REAL)''')
    conn.commit()
    conn.close()

def insert_ratings(rating_list):
    for tup in rating_list:
        if tup[1] is None:
            print(f"No ratings found for '{tup[0]}'. Skipping insertion.")
            return
    conn = sqlite3.connect('ratings.db')
    cur = conn.cursor()
    cur.execute('''INSERT OR REPLACE INTO 'Open Library Ratings' (rating) VALUES= (?)''', (rating_list))
    conn.commit()
    conn.close()

movie_adaptations = get_movie_titles_from_books(3)

create_database()
conn = sqlite3.connect('ratings.db')
cur = conn.cursor()
