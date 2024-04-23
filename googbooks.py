import requests
import json
import unittest
import os
import re
import sqlite3
from fuzzywuzzy import fuzz

def read_api_key(file):
    with open(file, "r") as key_file:
        key = key_file.read()
    return key

API_KEY = read_api_key("googbooks_key.txt")
    
def create_googlebooks_ratings_table():
    conn = sqlite3.connect('ratings.db')
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS 'GoogleBooks Ratings'
                 (title_id INTEGER PRIMARY KEY,
                  googlebooks_rating REAL,
                  FOREIGN KEY (title_id) REFERENCES 'Movie Ratings'(title_id))''')
    conn.commit()
    conn.close()

def insert_googlebooks_rating(title_id, googlebooks_rating):
    conn = sqlite3.connect('ratings.db')
    cur = conn.cursor()
    cur.execute('''INSERT OR REPLACE INTO 'GoogleBooks Ratings' (title_id, googlebooks_rating) VALUES (?, ?)''', (title_id, googlebooks_rating))
    conn.commit()
    conn.close()

def get_book_ratings(title):
    query_title = '"' + title.replace(" ", "+") + '"'
    url = f"https://www.googleapis.com/books/v1/volumes?q=title:{query_title}&key={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = json.loads(response.text)
        max_ratio = 0
        rating = None
        most_alike_title = ""
        if 'items' in data:
            for item in data['items']:
                if 'volumeInfo' in item and 'averageRating' in item['volumeInfo']:
                    current_title = item['volumeInfo']['title'].replace(" ", "+")
                    check_title = title.replace(" ", "+")
                    current_ratio = fuzz.ratio(check_title.lower(), current_title.lower())
                    if current_ratio > max_ratio:
                        most_alike_title = current_title
                        max_ratio = current_ratio
                        rating = item['volumeInfo']['averageRating']
                        if current_ratio == 100:
                            break
        # print(f"Title: {title}  |  Closest Title: {most_alike_title.replace('+', ' ')}  |  Max Ratio: {max_ratio}\n")
        return rating
    return None

# def find_closest_title(title):
#     conn = sqlite3.connect('ratings.db')
#     cur = conn.cursor()
#     cur.execute('''SELECT title FROM 'Movie Ratings' ORDER BY title_id''')
#     titles = [row[0] for row in cur.fetchall()]
#     ratio_title_pairs = [(fuzz.partial_ratio(title, title_in_db), title_in_db) for title_in_db in titles]
#     closest_titles = [pair[1] for pair in sorted(ratio_title_pairs, reverse=True)]
#     for closest_title in closest_titles:
#         cur.execute('''SELECT title_id FROM 'Movie Ratings' WHERE title = ?''', (closest_title,))
#         row = cur.fetchone()
#         if row:
#             conn.close()
#             return closest_title
#     conn.close()
#     return None

# def find_closest_title_with_rating(title):
#     conn = sqlite3.connect('ratings.db')
#     cur = conn.cursor()
#     cur.execute('''SELECT title FROM 'Movie Ratings' ORDER BY title_id''')
#     titles = [row[0] for row in cur.fetchall()]
#     ratio_title_pairs = [(fuzz.partial_ratio(title, title_in_db), title_in_db) for title_in_db in titles]
#     closest_titles = [pair[1] for pair in sorted(ratio_title_pairs, reverse=True)]
#     for closest_title in closest_titles:
#         cur.execute('''SELECT title_id FROM 'Movie Ratings' WHERE title = ?''', (closest_title,))
#         row = cur.fetchone()
#         if row:
#             title_id = row[0]
#             rating = get_book_ratings(closest_title)
#             if rating is not None:
#                 conn.close()
#                 return closest_title
#     conn.close()
#     return None

def main():
    create_googlebooks_ratings_table()
    conn = sqlite3.connect('ratings.db')
    cur = conn.cursor()
    # cur.execute('''SELECT title FROM 'Movie Ratings' ORDER BY title_id''')
    cur.execute('''
    SELECT MR.title
    FROM 'Movie Ratings' AS MR
    LEFT JOIN 'GoogleBooks Ratings' AS GB ON MR.title_id = GB.title_id
    WHERE GB.title_id IS NULL
    ''')
    title_list = [row[0] for row in cur.fetchall()]
    # last_25_titles = title_list[-25:]
    for title in title_list:
        # Retrieve title_id for the movie from Movie Ratings table
        cur.execute('''SELECT title_id FROM 'Movie Ratings' WHERE title = ?''', (title,))
        row = cur.fetchone()
        if row:
            title_id = row[0]
            rating = get_book_ratings(title)
            insert_googlebooks_rating(title_id, rating)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()