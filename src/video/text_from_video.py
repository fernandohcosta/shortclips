import json
import cv2
import numpy as np
from PIL import Image
import pytesseract

def get_text_from_video(run_folder, video_path, step=1):
    """Get text from video frames and returns a dictionary with the time in seconds as key"""
    video = cv2.VideoCapture(video_path)
    results = {}
    fps = video.get(cv2.CAP_PROP_FPS)  
    frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count/fps
    print(f"{duration }")
    for time in np.arange(0, duration, step):
        frame_id = int(fps*time)
        video.set(cv2.CAP_PROP_POS_FRAMES, frame_id)
        ok, frame = video.read()
        if ok:
            img = Image.fromarray(frame)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # todo: create a method to detect if the image has any text before passing to tesseract
            texts = pytesseract.image_to_string(img)
            texts = texts.replace("\n", " ")
            # todo: create a method to check if the text makes sense
            results[time] = texts
    
    json_object = json.dumps(results, indent=4)
    with open(run_folder / "ocr.json", "w") as outfile:
        outfile.write(json_object)
        
    return results