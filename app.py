from datetime import datetime
from pathlib import Path
import os

from flask import (
    Flask, 
    jsonify,
    request,
    json
)

from src.audio.extract_audio import download_audio_from_yotube
from src.audio.transcription import get_transcription
from src.text.sentence_transformer import define_topic
from src.text.segmentation import segment_transcription_simplified
from src.video.cut_video import save_shortclips
from src.video.save_video import save_video
from src.webscraping.site_scraping import get_website_texts


def create_app(test_config=None ):
    # create the app
    app = Flask(__name__)

    # Simple route to check if it is working
    @app.route('/')
    def test_app(): 
        return jsonify({
           "status": "success",
            "message": "Working!"
        }) 
    
    @app.route('/createshortclips', methods=["POST"])
    def createshortclips():
        cwd = Path(os.getcwd())
        output_folder = cwd / 'outputs'
        current_time = datetime.now()
        formatted_time = current_time.strftime('%Y-%m-%d_%Hh%M')
        run_folder = output_folder / formatted_time
        run_folder.mkdir(parents=True, exist_ok=True)
        data = json.loads(request.data)
        website_url = data["website_url"]
        if ',' in website_url:
            website_url = website_url.split(',')
        video_url = data["video_url"]
        get_website_texts(website_url, run_folder)
        download_audio_from_yotube(video_url, run_folder)
        get_transcription(run_folder)
        # righ now, clusters is not used as it is loaded inside the functions
        clusters = segment_transcription_simplified(run_folder)
        define_topic(run_folder)
        save_video(video_url, run_folder)
        clips_folder = run_folder / 'clips'
        clips_folder.mkdir(parents=True, exist_ok=True)
        save_shortclips( run_folder, clips_folder)
        return jsonify({
           "status": "success",
            "message": "Process finished!"
        }) 

    return app 


APP = create_app()


if __name__ == '__main__':
    APP.run(host='0.0.0.0', port=5000, debug=True)