import imdb
import urllib.parse
from application.models import Movie, Group
from bs4 import BeautifulSoup
import requests


access = imdb.Cinemagoer()


# The cover url returned from the search functions search_movies or get_movie_details below
# is low resolution one. To get a high resolution we can modify the url as below
def update_movie_cover(url):
    try:
        idx = url.find('_')
        cover = url[:idx] + '_V1_SX420.jpg'
    except ValueError:
        cover = url

    return cover


# Getting movie details based on movie name as parameter
def search_movies(movie_name):
    try:
        movies = access.search_movie(movie_name)
    except:
        movies = []
    if len(movies) == 0:
        return None
    movies_info = []
    for i in range(0, len(movies)):
        if i > 20:
            break
        else:
            try:
                year = movies[i]['year']
            except Exception:
                year = 0000
            try:
                cover = movies[i]['cover url']
                cover = update_movie_cover(cover)
            except Exception:
                cover = None
            info = {
                "title": movies[i]['title'],
                "year": year,
                "cover": cover,
                "id": movies[i].movieID,
                "url": access.get_imdbURL(movies[i])
                # "genres": genres
            }
            movies_info.append(info)

    return movies_info


# Getting movie details based on its IMDB Id
def get_movie_details(imdb_id):
    movie = access.get_movie(imdb_id)
    name = movie['title']
    cover = movie['cover url']
    cover_url = update_movie_cover(cover)
    access.update(movie)
    plot = get_plot(imdb_id)
    genre = movie['genres'][0]

    return name, cover_url, plot, genre


# Querying group, MovieGroups to get Movie ids, then finally Movie table to get Movie details
def get_group_movies(group_id):
    group = Group.query.filter_by(invite_token=group_id).first()
    # below query returns all the combination of group_id and movie_id from MovieGroups Table
    # which has a relationship with Group through group.id
    # so here results might looks like 1-3; 1-6; 1-19(1 being Group id)(3,6,9 -- Movie ids)
    g_movies = group.group_movies.all()
    movies_info = []

    for i in g_movies:
        # Now we query Movie table by using movie_id s returned above
        movie = Movie.query.get(i.movie_id)

        info = {
            "id": i.movie_id,
            "title": movie.name,
            "cover": movie.cover_url,
            "imdb_id": movie.imdb_id,
            "plot": movie.plot,
            "url": 'https://www.imdb.com/title/tt' + movie.imdb_id + '/',
            "genre": movie.genre
        }
        movies_info.append(info)

    return movies_info


def get_plot(imdb_id):
    url = 'https://www.imdb.com/title/tt' + str(imdb_id) + '/'
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    plot = soup.find("span", attrs={'data-testid': 'plot-l'}).text
    return plot


def get_wa_link(token):
    url = f"https://cinepal.herokuapp.com/invite/{token}"
    text = f"""Hello,
This is about a website where we can add movies and review together.
Come on, join and add your favourite movies at {url}"""
    urlencodedtext = urllib.parse.quote(text, safe="")
    wa_link = f"https://wa.me/?text={urlencodedtext}"
    return wa_link
