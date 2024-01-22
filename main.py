
from flask import (
    Flask, 
    jsonify
)

from src.audio.extract_audio import download_audio_from_yotube
from src.audio.transcription import get_transcription
from src.text.segmentation import segment_transcription
from src.video.cut_video import save_shortclips
from src.webscraping.site_scraping import get_website_texts


def run(config):

    video_url = 'https://www.youtube.com/watch?v=SFPUUsptIE0'
    website_url = ""
    original_video_path = ""
    output_path = ""
    download_audio_from_yotube(video_url)
    get_transcription()
    clusters = segment_transcription()
    get_website_texts(website_url)
    save_shortclips(original_video_path, output_path, clusters)
 



# Function that create the app 
def create_app(test_config=None ):
    # create and configure the app
    app = Flask(__name__)

    # Simple route
    @app.route('/')
    def testapp(): 
        return jsonify({
           "status": "success",
            "message": "Working!"
        }) 
    
    @app.rout('/createshortclips')
    def createshortclips(website_url, video_url):
        #video_url = 'https://www.youtube.com/watch?v=SFPUUsptIE0'
        download_audio_from_yotube(video_url)
        get_transcription()
        clusters = segment_transcription()
        get_website_texts(website_url)
        save_shortclips(clusters)


    return app 


APP = create_app()


if __name__ == '__main__':

    # APP.run(host='0.0.0.0', port=5000, debug=True)
    APP.run(debug=True)