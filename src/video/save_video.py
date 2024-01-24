from pytube import YouTube

def save_video(video_url, run_folder):
    yt = YouTube(video_url)
    yt.streams.filter(file_extension='mp4', resolution='720')
    stream = yt.streams.get_by_itag(22)
    stream.download(output_path=run_folder, filename='video.mp4')
