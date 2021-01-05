from base64 import b64encode
from mysql.connector import connection
from spotipy.oauth2 import SpotifyOAuth
import spotipy
import requests
from base64 import b64encode
from flask import Flask, Response, render_template
import os
import random
import mysql.connector

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")
MYSQL_HOST = os.getenv("HOST")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
TABLE_NAME = os.getenv("TABLE_NAME")

app = Flask(__name__)

def getWrapped():
    connection = mysql.connector.connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=DB_NAME)
    pointer = connection.cursor()

    query = "SELECT SUM(duration_ms * count)/1000/60 FROM {TABLE}".format(TABLE=TABLE_NAME)
    pointer.execute(query)
    wrapped = pointer.fetchone()
    
    return int(wrapped[0])

def getWrappedBadge(wrapped):
    url = "https://img.shields.io/badge/Wrapped-{MINUTES}-success?style=plastic&labelColor=123456&logoColor=white&logo=spotify".format(MINUTES=wrapped)
    badge = getImage(url)
    return badge

def getCoffeerBadge(coffees, beers):
    url = "https://img.shields.io/badge/{COFFEES}%20coffees%20%E2%98%95-{BEERS}%20beers%20%F0%9F%8D%BB-success?style=plastic&labelColor=123456".format(COFFEES=coffees, BEERS=beers)
    badge = getImage(url)
    return badge

def getLastPlayedSong(spotify):
    song = spotify.current_user_recently_played()["items"][random.randint(0, 20)]["track"]
    return song

def getSongFeatures(spotify, track_id):
    features = spotify.audio_features(track_id)[0]
    danceability = int(features["danceability"] * 255)
    energy = int(features["energy"] * 255)
    valence = int(features["valence"] * 255)

    return danceability, energy, valence

def getSong(spotify):
    return spotify.currently_playing()

def generateBars(barCount):
    barCSS = ""
    left = 0
    for i in range(1, barCount + 1):
        anim = random.randint(1000, 1350)
        barCSS += (
            ".bar:nth-child({})  {{ left: {}px; animation-duration: {}ms; }}".format(
                i, left, anim
            )
        )
        left += 4
    return barCSS

def getBaseCardData(title, text, cover, images):

    cover = getCover(cover)

    badges = ""

    for image in images:
        try:
            badge = getCover(image)
        except:
            badge = getCoffeerBadge(image['Coffees'], image['Beers'])
        badges += "<img src='data:image/svg+xml;base64,{BADGE}'></img>".format(BADGE=badge)


    data = {
        "title": title,
        "text": text,
        "cover": cover,
        "images": badges
    }

    return data


def getAltCardData(title, cover, images):

    cover = getCover(cover)
    
    badges = ""
    
    for image in images:
        badge = getCover(image)
        badges += "<img src='data:image/svg+xml;base64,{BADGE}'></img>\n".format(BADGE=badge)

    data = {
        "title": title,
        "cover": cover,
        "images": badges
    }

    return data

def getMediaCardData(spotify):
    
    song = getSong(spotify)

    if song is None or song["is_playing"] is False:
        contentBar = ""
        barCSS = ""
        song = getLastPlayedSong(spotify)
        danceability = 255
        energy = 255
        valence = 255
    else:
        song = song["item"]
        barCount = 65
        contentBar = ""
        for bar in range(barCount):
            contentBar += "<div class='bar'></div>\n"
        barCSS = generateBars(barCount)
        track_id = song["id"]
        danceability, energy, valence = getSongFeatures(spotify, track_id)
    album_cover = getImage(song["album"]["images"][1]["url"])
    
    '''
    images_name = [
        "media/wrapped.svg"
    ]
    images = ""
    for image_name in images_name:
        image = getCover(image_name)
        images += "<img src='data:image/svg+xml;base64,{IMAGE}'></img>".format(IMAGE=getWrappedBadge(getWrapped()))
    '''
    images = "<img src='data:image/svg+xml;base64,{IMAGE}'></img>".format(IMAGE=getWrappedBadge(970))
    artist = song["artists"][0]["name"].replace("&", "&amp;")
    track = song["name"].replace("&", "&amp;")
    link = song["external_urls"]["spotify"]

    data = {
        "link": link,
        "title": track,
        "text": artist,
        "cover": album_cover,
        "images": images,
        "contentBar": contentBar,
        "barCSS": barCSS,
        "danceability": danceability,
        "energy": energy,
        "valence": valence
    }
    return data

def getImage(url):
    response = requests.get(url)
    return b64encode(response.content).decode("ascii")

def getCover(file_name):
    with open(file_name, "rb") as file:
        cover = b64encode(file.read()).decode("ascii")
    return cover

def makeCard(card_template, card_data):
    return render_template(card_template, **card_data)


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def catch_all(path):

    mode = "light"

    auth_manager = SpotifyOAuth(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET, redirect_uri=SPOTIFY_REDIRECT_URI, scope='user-read-currently-playing user-read-recently-played')
    spotify = spotipy.Spotify(auth_manager=auth_manager)

    about_title = "Fermín Lassa"
    about_text = "I'm an IT student that ❤️ coding 👨‍💻 and beers 🍻"
    about_cover = "media/my_octocat.png"
    about_images = [{'Coffees': 2, 'Beers': 3}]

    about_data = getBaseCardData(about_title, about_text, about_cover, about_images)
    about_card = makeCard("base_{MODE}.html.j2".format(MODE=mode), about_data)

    skills_title = "Skills"
    skills_cover = "media/skills.webp"
    skills_images = [
        "media/java.svg",
        "media/python.svg",
        "media/mysql.svg",
        "media/html.svg",
        "media/css.svg",
        "media/php.svg",
        "media/javascript.svg",
        "media/cpp.svg",
        "media/bash.svg"
    ]

    skills_data = getAltCardData(skills_title, skills_cover, skills_images)
    skills_card = makeCard("alt_{MODE}.html.j2".format(MODE=mode), skills_data)

    education_title = "Telecommunication Engineering"
    education_text = """UPNA
                        <br></br>
                        09/2015 - 06/2020
                     """
    education_cover = "media/upna.png"
    education_images = ["media/pamplona.svg"]

    education_data = getBaseCardData(education_title, education_text, education_cover, education_images)
    education_card = makeCard("base_{MODE}.html.j2".format(MODE=mode), education_data)

    experience_title = "Backend Developer"
    experience_text = """livEvent
                         <br></br>
                         09/2019 - 01/2020
                      """
    experience_cover = "media/livEvent_alt.jpg"
    experience_images = ["media/pamplona.svg"]

    experience_data = getBaseCardData(experience_title, experience_text, experience_cover, experience_images)
    experience_card = makeCard("base_{MODE}.html.j2".format(MODE=mode), experience_data)

    spotify_data = getMediaCardData(spotify)
    spotify_link = spotify_data["link"]
    spotify_card = makeCard("spotify_{MODE}.html.j2".format(MODE=mode), spotify_data)

    cards = {
        "about": b64encode(str.encode(about_card)).decode("ascii"),
        "about_link": "https://fermin.lassa.net",
        "skills": b64encode(str.encode(skills_card)).decode("ascii"),
        "skills_link": "https://github.com/lassa97",
        "education": b64encode(str.encode(education_card)).decode("ascii"),
        "education_link": "https://www.unavarra.es/en/sites/grados/informatica-y-telecomunicacion/ingenieria-telecomunicacion/presentacion.html",
        "experience": b64encode(str.encode(experience_card)).decode("ascii"),
        "experience_link": "https://github.com/lassa97/livEvent",
        "spotify": b64encode(str.encode(spotify_card)).decode("ascii"),
        "spotify_link": spotify_link
    }

    slider = render_template("main.html.j2", **cards)

    resp = Response(slider, mimetype="image/svg+xml")
    resp.headers["Cache-Control"] = "s-maxage=1"

    return resp


if __name__ == "__main__":
    app.run(debug=True)
