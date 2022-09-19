import imdb
import urllib.parse
from application.models import Movie, Group


access = imdb.Cinemagoer()


def update_movie_cover(url):
    try:
        idx = url.find('_')
        cover = url[:idx] + '_V1_SX420.jpg'
    except ValueError:
        cover = url

    return cover


def search_movies(movie_name):
    try:
        movies = access.search_movie(movie_name)
    except:
        pass
    if len(movies) == 0:
        return None
    movies_info = []
    for i in range(0, len(movies)):
        if i > 20:
            break
        else:
            cover = movies[i]['cover url']
            cover = update_movie_cover(cover)
            try:
                year = movies[i]['year']
            except Exception:
                pass
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


def get_movie_details(imdb_id):
    movie = access.get_movie(imdb_id)
    name = movie['title']
    cover = movie['cover url']
    cover_url = update_movie_cover(cover)
    access.update(movie)
    plot = movie['plot'][0]
    genre = movie['genres'][0]

    return name, cover_url, plot, genre


def get_group_movies(group_id):
    group = Group.query.filter_by(invite_token=group_id).first()
    g_movies = group.group_movies.all()
    movies_info = []

    for i in g_movies:
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


def get_wa_link(token):
    url = f"https://cine-pals.herokuapp.com/invite/{token}"
    text = f"""Hello,
This is about a website where we can add movies and review together which we like.
Come on, join and add your favourite movies at {url}"""
    urlencodedtext = urllib.parse.quote(text, safe="")
    wa_link = f"https://wa.me/?text={urlencodedtext}"
    return wa_link
