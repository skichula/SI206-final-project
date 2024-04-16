import requests
import json
import unittest
import os
import re
import sqlite3
# from omdb import get_movie_titles_from_books

def read_api_key(file):
    with open(file, "r") as key_file:
        key = key_file.read()
    return key

API_KEY = read_api_key("googbooks_key.txt")

def convert_to_decimal(value):
    try:
        # Match floating-point numbers or integers
        match = re.search(r'(\d+(\.\d+)?)', value)
        if match:
            if float(match.group()) < 10:
                return round(float(match.group())/10, 2)
            if float(match.group()) > 10:
                return round(float(match.group())/100, 2)
        else:
            return None
    except Exception as e:
        print(f"Error converting to decimal: {e}")
        return None

def get_book_ratings(title):
    url = f"https://www.googleapis.com/books/v1/volumes?q=flowers&maxResults=25&key={API_KEY}"
    print(url)
    response = requests.get(url)
    if response.status_code == 200:
        data = json.loads(response.text)
        if data['Response'] == 'True':
            print("hello")
            # title = movie_data['Title']
            # ratings = movie_data['Ratings']
            # rating_decimals = {}
            # for rating in ratings:
            #     source = rating['Source']
            #     value = rating['Value']
            #     decimal_value = convert_to_decimal(value)
            #     if decimal_value is not None:
            #         rating_decimals[source] = decimal_value
            # return title, rating_decimals
            pass
        else:
            # return "Error: Movie not found", None
            pass
    else:
        # return "Error: Unable to access API", None
        pass

# def add_to_database():
#     conn = sqlite3.connect('ratings.db')
#     cur = conn.cursor()
#     cur.execute('''CREATE TABLE IF NOT EXISTS 'Google Books Ratings'
#                  (title_id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT UNIQUE, imdb REAL, rotten_tomatoes REAL, metacritic REAL)''')
#     conn.commit()
#     conn.close()

# def insert_ratings(title, ratings):
#     if ratings is None:
#         print(f"No ratings found for '{title}'. Skipping insertion.")
#         return
#     conn = sqlite3.connect('movie_ratings.db')
#     cur = conn.cursor()
#     cur.execute('''INSERT OR REPLACE INTO 'Google Books Ratings' (title, imdb, rotten_tomatoes, metacritic) VALUES (?, ?, ?, ?)''', (title, ratings.get('Internet Movie Database', None), ratings.get('Rotten Tomatoes', None), ratings.get('Metacritic', None)))
#     conn.commit()
#     conn.close()

#Running
# movie_adaptations = get_movie_titles_from_books(3)
# print(movie_adaptations)

# if not os.path.exists('ratings.db'):
#     add_to_database()

# conn = sqlite3.connect('ratings.db')
# cur = conn.cursor()
# cur.execute('''CREATE TABLE IF NOT EXISTS 'Google Books Ratings'
#              (title_id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT UNIQUE, imdb REAL, rotten_tomatoes REAL, metacritic REAL)''')


# cur.execute('''SELECT title FROM 'Google Books Ratings' ''')
# existing_titles = set(row[0] for row in cur.fetchall()) # Retrieve the titles of movies already in the database

# new_movies = []
# for title in movie_adaptations:
#     if title not in existing_titles:
#         new_movies.append(title)
# for title in new_movies[:26]:  # Limit to the first 25 new movies
#     ratings_output = get_book_ratings(title)
#     insert_ratings(title, ratings_output[1])

# conn.close()