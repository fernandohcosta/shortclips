import json

from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.video.io.VideoFileClip import VideoFileClip


def _save_clip(original_video_path, starttime, endtime, run_folder, clip_name):
    targetname = clip_name + ".mp4"
    input_video_path = original_video_path
    clips_folder = run_folder / "clips"
    output_video_path = clips_folder / targetname

    with VideoFileClip(str(input_video_path)) as video:
        new = video.subclip(starttime, endtime+0.1)
        new.write_videofile(str(output_video_path), audio_codec='aac')


def save_shortclips(run_folder, output_path):
    with open(run_folder / "clusters.json", "r") as f:
        clusters = json.load(f)
    original_video_path = run_folder / 'video.mp4'
    clip_topics = {}
    for cluster in clusters:
        starttime = clusters[cluster]["start"]
        endtime = clusters[cluster]["end"]
        clip_topic = clusters[cluster]["topic"]

        if clip_topic not in clip_topics:
            clip_topics[clip_topic] = 0
        clip_topics[clip_topic] += 1
        clip_name =  clip_topic + f"_{clip_topics[clip_topic]}"

        _save_clip(original_video_path, starttime, endtime, run_folder , clip_name)