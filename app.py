from flask import Flask, request, jsonify, send_file, Response, redirect
import colorama
import requests
from debug import request_dump
import re
from api import Invidious
app = Flask(__name__)
colorama.init()
api_url = 'http://192.168.1.192/api/v2'
invidious = Invidious()
        
@app.route('/api/search', methods=['GET'])
def search():
    query = request.args.get('q')
    return invidious.search(query)

@app.route('/api/trending', methods=['GET'])
def trends():
    query = request.args.get('type')
    format = request.args.get('format')
    platform = request.args.get('platform')
    if platform == 'wii' and format == 'playlist':
       return url.trends(query)
    return invidious.trends(query)
    
@app.route('/api/popular', methods=['GET'])
def popular():
    format = request.args.get('format')
    platform = request.args.get('platform')
    if platform == 'wii' and format == 'playlist':
       return url.popular()
    return invidious.popular()

@app.route('/api/channels/<channel_id>/uploads', methods=['GET'])
def userUploads(channel_id):
    return invidious.user_uploads(channel_id)

@app.route('/api/playlists/<playlist_id>', methods=['GET'])
def playlist_(playlist_id):
    return invidious.playlist(playlist_id)

@app.route('/leanback_ajax', methods=['GET'])
def leanback_ajax():
    action_featured = request.args.get('action_featured')
    action_environment = request.args.get('action_environment')
    p = request.args.get('p')
    client = request.args.get('client')
    lang = request.args.get('lang')
    request_dump(request)
    
    supportedLang = ['en','es','fr','de','ja','nl','it']

    if action_featured == '1' and client == 'lblwii' and lang in supportedLang:
        title_trends = {
            'en': 'Trending',
            'es': 'Tendencias',
            'fr': 'Tendance',
            'de': 'Im Trend',
            'ja': 'トレンド',
            'nl': 'Populair',
            'it': 'Tendenza'
        }
        
        title_music = {
            'en': 'Music',
            'es': 'Música',
            'fr': 'Musique',
            'de': 'Musik',
            'ja': '音楽',
            'nl': 'Muziek',
            'it': 'Musica'
        }
        
        title_gaming = {
            'en': 'Gaming',
            'es': 'Juegos',
            'fr': 'Jeux vidéo',
            'de': 'Gaming',
            'ja': 'ゲーム',
            'nl': 'Games',
            'it': 'Giochi'
        }
        
        title_fa = {
            'en': 'Film & Animation',
            'es': 'Películas y TV',
            'fr': 'Films et séries TV',
            'de': 'Filme & TV',
            'ja': 'ムービー＆TV',
            'nl': 'Films en tv',
            'it': 'Film e TV'
        }
        
        title_pop = {
            'en': 'Most Popular',
            'es': 'Más populares',
            'fr': 'Le plus populaire',
            'de': 'Am beliebtesten',
            'ja': '最も人気のある',
            'nl': 'Meest populair',
            'it': 'Più popolare'
        }

        response = {
            'sets': [
                {
                    'gdata_url': 'http://192.168.1.192:443/api/trending',
                    'thumbnail': 'http://192.168.1.192:443/api/thumbnails/trending',
                    'title': title_trends.get(lang)
                },
                {
                    'gdata_url': 'http://192.168.1.192:443/api/trending?type=Music',
                    'thumbnail': 'http://192.168.1.192:443/api/thumbnails/trending?type=Music',
                    'title': title_music.get(lang)
                },
                {
                    'gdata_url': 'http://192.168.1.192:443/api/trending?type=Gaming',
                    'thumbnail': 'http://192.168.1.192:443/api/thumbnails/trending?type=Gaming',
                    'title': title_gaming.get(lang)
                },
                {
                    'gdata_url': 'http://192.168.1.192:443/api/trending?type=Movies',
                    'thumbnail': 'http://192.168.1.192:443/api/thumbnails/trending?type=Movies',
                    'title': title_fa.get(lang)
                },
                {
                    'gdata_url': 'http://192.168.1.192:443/api/popular',
                    'thumbnail': 'http://192.168.1.192:443/api/thumbnails/popular',
                    'title': title_pop.get(lang)
                }
            ]
        }
        return jsonify(response), 200
    elif p == 'p':
        return '', 204       
    else:
        return "For right now, this ajax for leanback is only available for the Wii client.", 404
    
def fetch_and_serve_trending_thumbnail(type=None):
    if type:
        feed_url = f"http://192.168.1.192:443/api/trending?type={type}"
    else:
        feed_url = "http://192.168.1.192:443/api/trending"

    print('Downloading feed from:', feed_url)

    try:
        response = requests.get(feed_url)
        response.raise_for_status()
        data = response.text

        thumbnail_match = re.search(r"<media:thumbnail yt:name='hqdefault' url='(.*?)'", data)
        thumbnail_url = thumbnail_match.group(1) if thumbnail_match else None

        if thumbnail_url:
            return redirect(thumbnail_url, code=302)
        else:
            default_image_url = 'http://i.ytimg.com/vi/e/0.jpg'
            return redirect(default_image_url, code=302)
    except Exception as e:
        print("Error processing feed data:", e)
        return "Error processing feed data", 500

@app.route('/api/thumbnails/trending', methods=['GET'])
def trending_thumbnail():
    type = request.args.get('type')
    return fetch_and_serve_trending_thumbnail(type)
    
def fetch_and_serve_popular_thumbnail(type=None):
    pop_url = "http://192.168.1.192:443/api/popular"

    print('Downloading feed from:', pop_url)

    try:
        response = requests.get(pop_url)
        response.raise_for_status()
        data = response.text

        thumbnail_match = re.search(r"<media:thumbnail yt:name='hqdefault' url='(.*?)'", data)
        thumbnail_url = thumbnail_match.group(1) if thumbnail_match else None

        if thumbnail_url:
            return redirect(thumbnail_url, code=302)
        else:
            default_image_url = 'http://i.ytimg.com/vi/e/0.jpg'
            return redirect(default_image_url, code=302)
    except Exception as e:
        print("Error processing feed data:", e)
        return "Error processing feed data", 500
    
def fetch_and_serve_channel_uploads_thumbnail(channel_id):
    channel_uploads_url = f"http://192.168.1.192:443/api/channels/{channel_id}/uploads"
    print('Downloading feed from:', channel_uploads_url)
    try:
        response = requests.get(channel_uploads_url)
        response.raise_for_status()
        data = response.text
        thumbnail_match = re.search(r"<media:thumbnail yt:name='hqdefault' url='(.*?)'", data)
        thumbnail_url = thumbnail_match.group(1) if thumbnail_match else None
        if thumbnail_url:
            return redirect(thumbnail_url, code=302)
        else:
            default_image_url = 'http://i.ytimg.com/vi/e/0.jpg'
            return redirect(default_image_url, code=302)
    except Exception as e:
        print("Error processing feed data:", e)
        return "Error processing feed data", 500

@app.route('/api/thumbnails/channels/<channel_id>/uploads', methods=['GET'])
def channel_uploads_thumbnail(channel_id):
    return fetch_and_serve_channel_uploads_thumbnail(channel_id)

@app.route('/api/thumbnails/popular', methods=['GET'])
def popular_thumbnail():
    type = request.args.get('type')
    return fetch_and_serve_popular_thumbnail(type)

if __name__ == '__main__':
    app.run(debug=True, host='', port='')