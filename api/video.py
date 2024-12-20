from modules import get
from flask import Blueprint, Flask, request, redirect, render_template, Response, send_file, stream_with_context
import config
from modules.logs import text
import requests

video = Blueprint("video", __name__)

def error():
    return "",404

# featured videos
# 2 alternate routes for popular page and search results
@video.route("/feeds/api/standardfeeds/<regioncode>/<popular>")
@video.route("/feeds/api/standardfeeds/<popular>")
def frontpage(regioncode="US", popular=None):
    url = request.url_root
    # trending videos categories
    # the menu got less because of youtube removing it.
    apiurl = config.URL + "/api/v1/trending?region=" + regioncode
    if popular == "most_popular_Film":
        apiurl = f"{config.URL}/api/v1/trending?type=Movies&region={regioncode}"
    if popular == "most_popular_Games":
        apiurl = f"{config.URL}/api/v1/trending?type=Gaming&region={regioncode}"
    if popular == "most_popular_Music":
        apiurl = f"{config.URL}/api/v1/trending?type=Music&region={regioncode}"    

    # fetch api from invidious
    data = get.fetch(apiurl)
    
    if data:

        # print logs if enabled
        if config.SPYING == True:
            text("Region code: " + regioncode)

        # Classic YT path
        if popular == "recently_featured" or popular == "most_viewed" or popular == "top_rated":
            # get template
            return get.template('classic/featured.jinja2',{
                'data': data[:15],
                'unix': get.unix,
                'url': url
            })
        
        # Google YT
        return get.template('featured.jinja2',{
            'data': data[:config.FEATURED_VIDEOS],
            'unix': get.unix,
            'url': url
        })

    return error()

# search for videos
@video.route("/feeds/api/videos")
@video.route("/feeds/api/videos/")
def search_videos():
    url = request.url_root
    user_agent = request.headers.get('User-Agent')
    query = request.args.get('q')

    # remove space character
    search_keyword = query.replace(" ", "%20")
    
    # print logs if enabled
    if config.SPYING == True:
        text('Searched: ' + query)

    # search by videos
    data = get.fetch(f"{config.URL}/api/v1/search?q={search_keyword}&type=video")

    if data:

        # classic tube check
        if "YouTube v1.0.0" in user_agent:
            return get.template('classic/search.jinja2',{
                'data': data[:config.SEARCHED_VIDEOS],
                'unix': get.unix,
                'url': url
            })

        return get.template('search_results.jinja2',{
            'data': data[:config.SEARCHED_VIDEOS],
            'unix': get.unix,
            'url': url
        })

    return error()

# video's comments
# IDEA: filter the comments too?
@video.route("/api/videos/<videoid>/comments")
def comments(videoid):
    url = request.url_root
    # fetch invidious comments api
    data = get.fetch(f"{config.URL}/api/v1/comments/{videoid}?sortby={config.SORT_COMMENTS}")
    
    if data:

        return get.template('comments.jinja2',{
            'data': data['comments'],
            'unix': get.unix,
            'url': url
        })

    return error()

# returns backup.mp4 if an error occured while trying to get the video
@video.route("/geterrorvideo")
def geterrorvideo():
    return send_file("backup.mp4")

# fetches video from innertube.
@video.route("/getvideo/<video_id>")
def getvideo(video_id):
    try:
        data = get.fetch(f"{config.URL}/api/v1/videos/{video_id}")
        if not data:
            print("No data")
            return redirect("/geterrorvideo", 307)
        if not config.MEDIUM_QUALITY:
            try:
                print("Not implemented, falling back to 360P")
            except:
                print("Failed to get HLS stream")
        # 360p if enabled
        output = redirect("/geterrorvideo", 307)
        size = -1
        for video in data["formatStreams"]:
            if "avc" in video["type"] and "mp4a" in video["type"]:
                res = int("".join(c for c in video["resolution"] if c.isnumeric()))
                if size == -1 or (size <= config.HLS_RESOLUTION and res > size) or (size > config.HLS_RESOLUTION and size <= res):
                    output = redirect(video["url"], 307)
                if (config.HLS_RESOLUTION == res):
                    return output
        return output
    except:
        print("Error Occured. Is the Invidious instance working?")
    return redirect("/geterrorvideo", 307)
