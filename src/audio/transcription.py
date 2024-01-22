import whisper
import json

def delete_replicas(list_of_dicts):
    idx = 1
    while idx < len(list_of_dicts):
        if list_of_dicts[idx]["text"] == list_of_dicts[idx-1]["text"]:
            del list_of_dicts[idx]
        idx += 1
    return list_of_dicts

def get_transcription(run_folder):
    model = whisper.load_model("medium.en")
    result = model.transcribe(str(run_folder / "audio.wav"))
    with open(run_folder / 'transcription.txt', 'w', encoding="utf-8") as f:
        f.write(result["text"])
    segments = delete_replicas(result["segments"])
    json_object = json.dumps(segments, indent=4)
    with open(run_folder / "segments.json", "w") as outfile:
        outfile.write(json_object)
