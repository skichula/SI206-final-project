import requests
import json
import unittest
import os
import re
import sqlite3
from omdb import get_movie_titles_from_books

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

def main():
    create_googlebooks_ratings_table()
    conn = sqlite3.connect('ratings.db')
    cur = conn.cursor()
    movie_adaptations = get_movie_titles_from_books(3)
    for title in movie_adaptations:
        # Retrieve title_id for the movie from Movie Ratings table
        cur.execute('''SELECT title_id FROM 'Movie Ratings' WHERE title = ?''', (title,))
        row = cur.fetchone()
        if row:
            title_id = row[0]
            rating = get_book_ratings(title)
            if rating is not None:
                # Insert Google Books rating along with the title_id
                insert_googlebooks_rating(title_id, rating)
        else:
            print(f"No title_id found for '{title}'. Skipping insertion.")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()