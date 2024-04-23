import requests
import json
import unittest
import os
import re
import sqlite3

from fuzzywuzzy import fuzz


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
                rating = book_info.get('ratings_average', "Null")
                rating_list.append((title, rating))
    return rating_list

def create_database():
    conn = sqlite3.connect('ratings.db')
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS 'Open Library Ratings'
                 (title_id INTEGER PRIMARY KEY AUTOINCREMENT, rating REAL)''')
    conn.commit()
    conn.close()
    
def find_best_match(title, cur):
    cur.execute('''SELECT title, title_id FROM "Movie Ratings"''')
    matches = []
    for row in cur.fetchall():
        title_in_table = row[0]
        title_id = row[1]
        similarity_ratio = fuzz.partial_ratio(title, title_in_table)
        # print(f'sarah title is {title_in_table}')
        matches.append((title_in_table, title_id, similarity_ratio))
    return max(matches, key=lambda x: x[2])[1] if matches else None

def insert_ratings(rating_list):
    conn = sqlite3.connect('ratings.db')
    cur = conn.cursor()
    
    for tup in rating_list:
        title = tup[0]
        rating = tup[1]
        
        title_id = find_best_match(title, cur)
        # print(f'emma title:{title} | sarah title:{title_id}')
        
        if title_id:
            cur.execute('''INSERT OR REPLACE INTO "Open Library Ratings" (title_id, rating) VALUES (?, ?)''', (title_id, rating))
        else:
            print(f"No matching title found for {title}")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_database()
    conn = sqlite3.connect('ratings.db')
    cur = conn.cursor()

    cur.execute('''SELECT title from "Movie Ratings" ORDER BY title_id''')
    movie_adaptations = [row[0] for row in cur.fetchall()]
    # print(movie_adaptations)
    book_titles = get_title(movie_adaptations)
    # print(book_titles)
    rating_list = get_book_ratings(book_titles)
    # print(ratings)

    insert_ratings(rating_list)
