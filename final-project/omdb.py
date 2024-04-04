import requests
import json
import unittest
import os
import re
import sqlite3

# #Right now, I have accessed the ombd api to get ratings and the imbd api to get movies that are book adaptations; the imbd data is used to create a list of all movie adaptations and this list is passed through the functions using the api to get the ratings for all of those movies (right now only accessing first page which is 50 movies); the database created is organized by the three different ratings, adding 25 titles at most at a time (still won't add more than 48)

def read_api_key(file):
    with open(file, "r") as key_file:
        key = key_file.read()
    return key

API_KEY = read_api_key("omdb_key.txt")

from imdb import IMDb

def get_movie_titles_from_books():
    ia = IMDb()
    search_results = ia.get_keyword('based-on-novel')
    movie_titles = []
    for movie in search_results:
        title = re.search(r'^([^()]+)', str(movie)).group(1)
        movie_titles.append(title.strip())
    return movie_titles

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

def get_movie_ratings(title):
    url = f"http://www.omdbapi.com/?apikey={API_KEY}&t={title}"
    response = requests.get(url)
    if response.status_code == 200:
        movie_data = json.loads(response.text)
        if movie_data['Response'] == 'True':
            title = movie_data['Title']
            ratings = movie_data['Ratings']
            rating_decimals = {}
            for rating in ratings:
                source = rating['Source']
                value = rating['Value']
                decimal_value = convert_to_decimal(value)
                if decimal_value is not None:
                    rating_decimals[source] = decimal_value
            return title, rating_decimals
        else:
            return "Error: Movie not found", None
    else:
        return "Error: Unable to access API", None

def create_database():
    conn = sqlite3.connect('movie_ratings.db')
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS 'Movie Ratings'
                 (title TEXT PRIMARY KEY, imdb REAL, rotten_tomatoes REAL, metacritic REAL)''')
    conn.commit()
    conn.close()

def insert_ratings(title, ratings):
    conn = sqlite3.connect('movie_ratings.db')
    cur = conn.cursor()
    cur.execute('''INSERT OR REPLACE INTO 'Movie Ratings' (title, imdb, rotten_tomatoes, metacritic)
                 VALUES (?, ?, ?, ?)''', (title, ratings.get('Internet Movie Database', None), ratings.get('Rotten Tomatoes', None), ratings.get('Metacritic', None)))
    conn.commit()
    conn.close()

#Running
movie_adaptations = get_movie_titles_from_books()

if not os.path.exists('movie_ratings.db'):
    create_database()

conn = sqlite3.connect('movie_ratings.db')
cur = conn.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS 'Movie Ratings'
             (title TEXT PRIMARY KEY, imdb REAL, rotten_tomatoes REAL, metacritic REAL)''')


cur.execute('''SELECT title FROM 'Movie Ratings' ''')
existing_titles = set(row[0] for row in cur.fetchall()) # Retrieve the titles of movies already in the database

new_movies = []
for title in movie_adaptations:
    if title not in existing_titles:
        new_movies.append(title)
for title in new_movies[:26]:  # Limit to the first 25 new movies
    ratings_output = get_movie_ratings(title)
    insert_ratings(title, ratings_output[1])

#optional printing statement
# cur.execute('''SELECT * FROM 'Movie Ratings' ''')
# for row in cur.fetchall():
#     print(f"Ratings for '{row[0]}': IMDb: {row[1]}, Rotten Tomatoes: {row[2]}, Metacritic: {row[3]}")

conn.close()