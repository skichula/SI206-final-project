import requests
import json
import unittest
import os
import re

#Right now, I have accessed the ombd api to get ratings and the imbd api to get movies that are book adaptations; the imbd data is used to run the code for all movies that fall into category of film adaptations (right now only printing first page which is 50 movies)

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

def get_movie_ratings(title):
    url = f"http://www.omdbapi.com/?apikey={API_KEY}&t={title}"
    response = requests.get(url)
    if response.status_code == 200:
        movie_data = json.loads(response.text)
        if movie_data['Response'] == 'True':
            title = movie_data['Title']
            ratings = movie_data['Ratings']
            rating_strings = []
            for rating in ratings:
                rating_strings.append(f"{rating['Source']}: {rating['Value']}")
            return (title, ', '.join(rating_strings))
        else:
            return "Error: Movie not found", None
    else:
        return "Error: Unable to access API", None

movie_adaptations = get_movie_titles_from_books()
#print(movie_adaptations)
for title in movie_adaptations:
    ratings_output = get_movie_ratings(title)
    if len(ratings_output[1]) > 0:
        print(f"Ratings for '{title}': {ratings_output[1]}")
    else:
        print(f"There is no rating for '{title}'.")