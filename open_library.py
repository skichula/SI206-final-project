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
    # print(movie_titles)
    return movie_titles

def get_title(movie_titles):
    book_list = []
    for movie_title in movie_titles:
        words = movie_title.split()
        title = '+'.join(words)
        book_list.append(title)
        # print(book_list)
    return book_list
    
def get_book_ratings(book_list):
    rating_list = []
    for title in book_list:
        url = f"https://openlibrary.org/search.json?title={title}"
        response = requests.get(url)
        if response.status_code == 200:
            book_data = json.loads(response.text)
            if 'docs' in book_data and len(book_data['docs']) > 0:
                book_info = book_data['docs'][0]
                # print(book_info)
                title = book_info.get('title', 0)
                rating = book_info.get('ratings_average', 0)
                rating_list.append([title, rating])
    return rating_list



def create_database():
    conn = sqlite3.connect('ratings.db')
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS 'Open Library Ratings'
                 (title_id INTEGER PRIMARY KEY AUTOINCREMENT, rating REAL)''')
    conn.commit()
    conn.close()

def insert_ratings(rating_list):
    conn =sqlite3.connect('ratings.db')
    cur = conn.cursor()
    # print(rating_list)
    for tup in rating_list:
        title = tup[0]
        rating = tup[1]
        # print(f'ratings for {tup[0]}: {tup[1]}')
        cur.execute('''SELECT title_id FROM "Movie Ratings" WHERE title = ?''', (title,))
        result = cur.fetchone()
        if result: 
            title_id = result[0]
            cur.execute('''INSERT OR REPLACE INTO 'Open Library Ratings' (title_id, rating) VALUES (?, ?)''', (title_id, rating))
        else:
            print(f"No matching title found for {title}")
    conn.commit()
    conn.close()

create_database()
conn = sqlite3.connect('ratings.db')
cur = conn.cursor()

movie_adaptations = get_movie_titles_from_books(1)
# print(movie_adaptations)
book_titles = get_title(movie_adaptations)
# print(book_titles)
ratings = get_book_ratings(book_titles)
# print(ratings)
insert_ratings(ratings[0:26])


# cur.execute('''SELECT title FROM 'Movie Ratings' ''')
# existing_titles = set(row[0] for row in cur.fetchall()) # Retrieve the titles of movies already in the database

# new_movies = []
# for title in movie_adaptations:
#     if title not in existing_titles:
#         new_movies.append(title)
# for title in new_movies[:26]:  # Limit to the first 25 new movies
#     ratings_output = get_movie_ratings(title)
#     insert_ratings(title, ratings_output[1], ratings_output[2])