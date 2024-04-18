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
        found = False
        rating = None
        for item in data['items']:
            if found:
                break
            if item['volumeInfo']['title'] == title:
                found = True
                if "averageRating" in item['volumeInfo']:
                    rating = item['volumeInfo']['averageRating']
    return rating

def find_closest_title(title):
    conn = sqlite3.connect('ratings.db')
    cur = conn.cursor()
    cur.execute('''SELECT title FROM 'Movie Ratings' ORDER BY title_id''')
    titles = [row[0] for row in cur.fetchall()]
    ratio_title_pairs = [(fuzz.partial_ratio(title, title_in_db), title_in_db) for title_in_db in titles]
    closest_titles = [pair[1] for pair in sorted(ratio_title_pairs, reverse=True)]
    for closest_title in closest_titles:
        cur.execute('''SELECT title_id FROM 'Movie Ratings' WHERE title = ?''', (closest_title,))
        row = cur.fetchone()
        if row:
            conn.close()
            return closest_title
    conn.close()
    return None

def get_rating_for_closest_title(title):
    query_title = '"' + title.replace(" ", "+") + '"'
    url = f"https://www.googleapis.com/books/v1/volumes?q=title:{query_title}&key={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = json.loads(response.text)
        for item in data['items']:
            if item['volumeInfo']['title'] == title:
                if "averageRating" in item['volumeInfo']:
                    return item['volumeInfo']['averageRating']
    return None

def main():
    create_googlebooks_ratings_table()
    conn = sqlite3.connect('ratings.db')
    cur = conn.cursor()
    cur.execute('''SELECT title FROM 'Movie Ratings' ORDER BY title_id''')
    title_list = [row[0] for row in cur.fetchall()]
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