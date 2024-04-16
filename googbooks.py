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
    query_title = '"' + title.replace(" ", "+") + '"'
    url = f"https://www.googleapis.com/books/v1/volumes?q=title:{query_title}&key={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = json.loads(response.text)
        found = False
        for item in data['items']:
            if found:
                break
            if item['volumeInfo']['title'] == title:
                found = True
                rating = item['volumeInfo']['averageRating']
        if not found:
            rating = -1

get_book_ratings("The Maze Runner")