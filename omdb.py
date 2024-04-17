import requests
import json
import unittest
import os
import re
import sqlite3

#Right now, I have accessed the ombd api to get ratings and the imbd api to get movies that are book adaptations; the imbd data is used to create a list of all movie adaptations and this list is passed through the functions using the api to get the ratings for all of those movies (right now we are accessing first 3 pages); the database created is organized by the three different ratings, adding 25 titles at most at a time; we join the genre table with the movies table to organize movies based on their primary genre (first one listed)

def read_api_key(file):
    with open(file, "r") as key_file:
        key = key_file.read()
    return key

API_KEY = read_api_key("omdb_key.txt")

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
            genres = movie_data['Genre']
            rating_decimals = {}
            for rating in ratings:
                source = rating['Source']
                value = rating['Value']
                decimal_value = convert_to_decimal(value)
                if decimal_value is not None:
                    rating_decimals[source] = decimal_value
            #print(title, rating_decimals, genres)
            return title, rating_decimals, genres
        else:
            return "Error: Movie not found", None, None
    else:
        return "Error: Unable to access API", None, None

def create_database():
    conn = sqlite3.connect('ratings.db')
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS 'Genres'
                 (genre_id INTEGER PRIMARY KEY AUTOINCREMENT, genre TEXT UNIQUE)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS 'Movie Ratings'
                 (title_id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT UNIQUE, imdb REAL, rotten_tomatoes REAL, metacritic REAL, genre_id INTEGER, FOREIGN KEY (genre_id) REFERENCES Genres(genre_id))''')
    conn.commit()
    conn.close()

# def insert_ratings(title, ratings, genres):
    
#     conn = sqlite3.connect('ratings.db')
#     cur = conn.cursor()
#     if genres is not None:
#         for genre in genres.split(', '):
#             #print(genre)
#             cur.execute('''INSERT OR IGNORE INTO 'Genres' (genre) VALUES (?)''', (genre,))
#     if ratings is None:
#         print(f"No ratings found for '{title}'. Skipping insertion.")
#         return
#     cur.execute('''INSERT OR REPLACE INTO 'Movie Ratings' (title, imdb, rotten_tomatoes, metacritic) VALUES (?, ?, ?, ?)''', (title, ratings.get('Internet Movie Database', None), ratings.get('Rotten Tomatoes', None), ratings.get('Metacritic', None)))
#     conn.commit()
#     conn.close()
def insert_ratings(title, ratings, genres):
    conn = sqlite3.connect('ratings.db')
    cur = conn.cursor()
    # Insert the first genre into the 'Genres' table
    if genres is not None:
        first_genre = genres.split(', ')[0]
        cur.execute('''INSERT OR IGNORE INTO 'Genres' (genre) VALUES (?)''', (first_genre,))
        # Retrieve the genre_id of the inserted genre
        cur.execute('''SELECT genre_id FROM 'Genres' WHERE genre = ?''', (first_genre,))
        genre_row = cur.fetchone()
        if genre_row:
            genre_id = genre_row[0]
        else:
            print(f"Error: Genre ID not found for '{first_genre}'. Skipping insertion.")
            return
    # Insert movie ratings into 'Movie Ratings' table
    if ratings is None:
        print(f"No ratings found for '{title}'. Skipping insertion.")
    else:
        cur.execute('''INSERT OR REPLACE INTO 'Movie Ratings' (title, imdb, rotten_tomatoes, metacritic, genre_id) VALUES (?, ?, ?, ?, ?)''', (title, ratings.get('Internet Movie Database', None), ratings.get('Rotten Tomatoes', None), ratings.get('Metacritic', None), genre_id))
    
    conn.commit()
    conn.close()

def get_movies_with_genres():
    conn = sqlite3.connect('ratings.db')
    cur = conn.cursor()
    cur.execute('''SELECT m.title, m.imdb, m.rotten_tomatoes, m.metacritic, g.genre FROM 'Movie Ratings' m JOIN 'Genres' g ON m.genre_id = g.genre_id''')
    rows = cur.fetchall()
    conn.close()
    return rows

if __name__ == "__main__":
    #Running
    movie_adaptations = get_movie_titles_from_books(3)

    create_database()
    conn = sqlite3.connect('ratings.db')
    cur = conn.cursor()

    cur.execute('''SELECT title FROM 'Movie Ratings' ''')
    existing_titles = set(row[0] for row in cur.fetchall()) # Retrieve the titles of movies already in the database

    new_movies = []
    for title in movie_adaptations:
        if title not in existing_titles:
            new_movies.append(title)
    for title in new_movies[:26]:  # Limit to the first 25 new movies
        ratings_output = get_movie_ratings(title)
        insert_ratings(title, ratings_output[1], ratings_output[2])


    movies_with_genres = get_movies_with_genres()
    # for movie in movies_with_genres:
        #print(movie)

    #optional printing statement
    cur.execute('''SELECT * FROM 'Movie Ratings' ''')
    for row in cur.fetchall():
        print(f"Ratings for '{row[1]}': IMDb: {row[2]}, Rotten Tomatoes: {row[3]}, Metacritic: {row[4]}, Genre ID: {row[5]}")

    conn.close()