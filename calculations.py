import sqlite3
import matplotlib.pyplot as plt
import numpy as np

def get_genres():
    conn = sqlite3.connect('ratings.db')
    cur = conn.cursor()
    cur.execute('''SELECT genre FROM Genres''')
    genres = [row[0] for row in cur.fetchall()]
    conn.close()
    return genres

def calculate_average_ratings(genre):
    conn = sqlite3.connect('ratings.db')
    cur = conn.cursor()

    # Match genre_id for the given genre
    cur.execute('''SELECT genre_id FROM 'Genres' WHERE genre = ?''', (genre,))
    genre_row = cur.fetchone()
    if genre_row:
        genre_id = genre_row[0]
    else:
        print(f"Error: Genre '{genre}' not found in the database.")
        conn.close()
        return None

    cur.execute('''SELECT imdb, rotten_tomatoes, metacritic FROM 'Movie Ratings' WHERE genre_id = ?''', (genre_id,))
    rows = cur.fetchall()

    total_imdb = 0
    total_rotten_tomatoes = 0
    total_metacritic = 0
    count_imdb = 0 
    count_rotten_tomatoes = 0
    count_metacritic = 0

    for row in rows:
        if row[0] is not None:
            total_imdb += row[0]
            count_imdb += 1
        else:
            total_imdb += 0
        if row[1] is not None:
            total_rotten_tomatoes += row[1]
            count_rotten_tomatoes += 1
        else:
            total_rotten_tomatoes += 0
        if row[2] is not None:
            total_metacritic += row[2]
            count_metacritic += 1
        else:
            total_metacritic += 0
    if count_imdb > 0:
        avg_imdb = round((total_imdb / count_imdb), 2)
    else:
        avg_imdb = None
    if count_rotten_tomatoes > 0:
        avg_rotten_tomatoes = round((total_rotten_tomatoes / count_rotten_tomatoes), 2)
    else:
        avg_rotten_tomatoes = None
    if count_metacritic > 0:
        avg_metacritic = round((total_metacritic / count_metacritic), 2)
    else:
        avg_metacritic = None
    conn.close()
    #print(avg_imdb, avg_rotten_tomatoes, avg_metacritic)
    return avg_imdb, avg_rotten_tomatoes, avg_metacritic

genres = get_genres()
for genre in genres:
    imdb_ratings, rotten_tomatoes_ratings, metacritic_ratings = calculate_average_ratings(genre)
    # print(f"The average ratings for {genre} movies are:")
    # print(f"IMDb: {imdb_ratings}")
    # print(f"Rotten Tomatoes: {rotten_tomatoes_ratings}")
    # print(f"Metacritic: {metacritic_ratings}")

def plot_movie_ratings_by_genre():
    bar_width = 0.25
    index = range(len(genres))

    # Collect average ratings for all genres
    imdb_ratings = []
    rotten_tomatoes_ratings = []
    metacritic_ratings = []

    for genre in genres:
        avg_imdb, avg_rotten_tomatoes, avg_metacritic = calculate_average_ratings(genre)
        if avg_imdb is not None:
            imdb_ratings.append(avg_imdb)
        else:
            imdb_ratings.append(0)
        if avg_rotten_tomatoes is not None:
            rotten_tomatoes_ratings.append(avg_rotten_tomatoes)
        else:
            rotten_tomatoes_ratings.append(0)
        if avg_metacritic is not None:
            metacritic_ratings.append(avg_metacritic)
        else:
            metacritic_ratings.append(0)
   
    fig, ax = plt.subplots()
    bar1 = ax.bar(index, imdb_ratings, bar_width, label='IMDb')
    bar2 = ax.bar([i + bar_width for i in index], rotten_tomatoes_ratings, bar_width, label="Rotten Tomatoes")
    bar3 = ax.bar([i + bar_width * 2 for i in index], metacritic_ratings, bar_width, label="Metacritic")

    ax.set_xlabel("Genres")
    ax.set_ylabel("Average Ratings")
    ax.set_title("Average Ratings by Genre")
    ax.set_xticks([i + bar_width for i in index])
    ax.set_xticklabels(genres, rotation=45)
    ax.legend()

    plt.tight_layout()
    plt.show()


def calculate_average_book_rating():
    conn = sqlite3.connect('ratings.db')
    cur = conn.cursor()

    # Joining the Open Library Ratings table and the Google Books Ratings table on title_id
    cur.execute('''
        SELECT MR.title, 
                MR.imdb as movie_rating,
               (OL.rating + GB.googlebooks_rating) / 2 AS average_rating
        FROM "Movie Ratings" as MR
        LEFT JOIN "Open Library Ratings" AS OL ON MR.title_id = OL.title_id
        LEFT JOIN "GoogleBooks Ratings" AS GB ON MR.title_id = GB.title_id
        WHERE MR.imdb IS NOT NULL AND OL.rating IS NOT NULL AND GB.googlebooks_rating IS NOT NULL
        LIMIT 10
    ''')

    average_ratings = cur.fetchall()
    # print(average_ratings)

    conn.close()
    return average_ratings

# calculate_average_book_rating()

def plot_compare_ratings():
    average_book_ratings = calculate_average_book_rating()

    # Extracting titles, movie ratings, and average book ratings from the fetched data
    book_titles, movie_ratings, average_book_ratings = zip(*average_book_ratings)

    # Creating a bar graph with two bars for each title
    bar_width = 0.35
    index = range(len(book_titles))

    fig, ax = plt.subplots()
    bar1 = ax.bar(index, movie_ratings, bar_width, label='Movie')
    bar2 = ax.bar([i + bar_width for i in index], average_book_ratings, bar_width, label="Book")

    ax.set_xlabel("Titles")
    ax.set_ylabel("Average Ratings")
    ax.set_title("Comparison of Average Ratings Between Books and Movies")
    ax.set_xticks([i + bar_width for i in index])
    ax.set_xticklabels(book_titles, rotation=45)
    ax.legend()

    plt.tight_layout()
    plt.show()

plot_compare_ratings()
# plot_movie_ratings_by_genre()
