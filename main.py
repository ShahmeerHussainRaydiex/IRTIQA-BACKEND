import uvicorn
from fastapi import FastAPI, HTTPException, Header
import requests
from pypexels import PyPexels


app = FastAPI()


@app.get("/check")
async def root():
    import ffmpeg

    input_background = ffmpeg.input('background.mp4')
    input_color = ffmpeg.input('test.mp4')
    input_alpha = ffmpeg.input('test.mp4')

    coloralpha = ffmpeg.filter([input_color, input_alpha], 'alphamerge')

    background_resized = \
        input_background.filter('scale2ref', 'main_w*max(iw/main_w, ih/main_h)', 'main_h*max(iw/main_w, ih/main_h)')[0]
    overlay = ffmpeg.overlay(background_resized, coloralpha, shortest=1, x='main_w/2-overlay_w/2', y='main_h-overlay_h')

    darset = overlay.filter('setdar', 'dar=a').filter('pad', 'ceil(iw/2)*2', 'ceil(ih/2)*2')[0]
    output = darset

    output = output.output('output.mp4', vcodec='libx264', crf=17, pix_fmt='yuv420p', strict='experimental',
                           acodec='copy')

    output.run()

    output.run()

    return {f"message": f"Hello World"}


API_KEY = "Wtp3BUo71YxFRAgWqIawy6BnpIDagOQtbh2YeUu4r6kKCmwwPXGhHIHS"


@app.get("/search/images")
async def search_images(query: str):
    headers = {
        "Authorization": f"{API_KEY}"
    }

    # Make a request to the Pexels API
    response = requests.get(f"https://api.pexels.com/v1/search?query={query}", headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Pexels API request failed")

    return response.json()


@app.get("/search/videos")
async def search_videos(query: str, per_page: int = 1):
    headers = {
        "Authorization": f"{API_KEY}"
    }

    # Make a request to the Pexels API
    response = requests.get(f"https://api.pexels.com/videos/search?query={query}&per_page={per_page}", headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Pexels API request failed")

    return response.json()


@app.get("/search/test")
async def search_videos(query: str, num_page: int = 1, per_page: int = 1):
    headers = {
        "Authorization": API_KEY
    }
    py_pexel = PyPexels(api_key=API_KEY)
    search_videos_page = py_pexel.videos_search(query=query, per_page=per_page)
    for video in search_videos_page.entries:
        print(video.id, video.user.get('name'), video.url)

        url = f"https://api.pexels.com/videos/videos/{video.id}"
        response = requests.get(url, headers=headers)
        data_url = 'https://www.pexels.com/video/' + str(video.id) + '/download'
        r = requests.get(data_url)
        print(r.headers.get('content-type'))
        with open(f'{video.id}.mp4', 'wb') as outfile:
            outfile.write(r.content)
    return {f"message": f"Downloaded videos"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)