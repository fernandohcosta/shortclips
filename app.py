
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
from src.text.segmentation import segment_transcription, segment_transcription_llm, segment_transcription_llm_test
from src.video.cut_video import save_shortclips
from src.video.save_video import save_video
from src.webscraping.site_scraping import get_website_texts
from src.text.sentence_transformer import define_topic



# Function that create the app 
def create_app(test_config=None ):
    # create and configure the app
    app = Flask(__name__)

    # Simple route
    @app.route('/')
    def test(): 
        return jsonify({
           "status": "success",
            "message": "Working!"
        }) 
    
    @app.route('/createshortclips', methods=["POST"])
    def createshortclips():
        #video_url = 'https://www.youtube.com/watch?v=SFPUUsptIE0'
        #url = "https://www.yuengling.com"
        
        cwd = Path(os.getcwd())
        output_folder = cwd / 'outputs'
        print(output_folder)
        current_time = datetime.now()
        formatted_time = current_time.strftime('%Y-%m-%d_%Hh%M')
        run_folder = output_folder / formatted_time
        run_folder = Path(r"D:\shortclips\outputs\2024-01-21_15h15")
        run_folder.mkdir(parents=True, exist_ok=True)
        data = json.loads(request.data)
        print(data)
        website_url = data["website_url"]
        if ',' in website_url:
            website_url = website_url.split(',')
        video_url = data["video_url"]

        download_audio_from_yotube(video_url, run_folder)
        get_transcription(run_folder)
        clusters = segment_transcription_llm_test(run_folder)
        get_website_texts(website_url, run_folder)
        define_topic(run_folder)
        save_video(video_url, run_folder)
        clips_folder = run_folder / 'clips'
        clips_folder.mkdir(parents=True, exist_ok=True)
        save_shortclips( run_folder, clips_folder)
        return 


    return app 


APP = create_app()


if __name__ == '__main__':

    APP.run(host='0.0.0.0', port=5000, debug=True)
    #APP.run(debug=True, )