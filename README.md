# shortclips
This repository is dedicated to creating automatic short clips from long videos.
This is a simplified process, but new features can be added as needed.

Currently, the configurations are hardcoded for simplicity.
Several files are saved in the outputs folder so the steps required to create the segments can be analyzed.

Basically, the process consists of transcribing the audio from the YouTube video, segmenting the transcription [1] and assigning topic names to each segment using sentence similarity. The titles of the texts obtained from the web scraping process are used as topic names, but it could be adjusted to use other methods such as Top2Vec.

There are some limitations right now, but this process can be adjusted and refined.

## File structure
```
|-app.py
|-dockerfile
|-README.md
|-requirements.txt
|-src
  |-audio
  |-text
  |-video
  |-webscraping
```

# How to run it
You can run it locally just creating a virtual environment and installing the requirements using:

```python -m pip install -r requirements.txt```

You can also create a docker image using:

``` build -t shortclips:1.0 .  ```

When starting the docker container, set the host port to 5000 and bind a local folder to the directory /app/outputs in the container so you can access the outputs of this app.

To make a call, just send a POST request with the URL (or a list of URLs) to the website and the URL to the corresponding YouTube video, for example:

```
curl -X POST -H "Content-type: application/json" -d "{\"website_url\" : \"https://page1.html, https://page2.html, https://page3.html\", \"video_url\" : \"https://www.youtube.com/video\"}" "0.0.0.0:5000/createshortclips"
```
If one page is passed, the web scrapper will look for all pages on the website, but this can be not optimal, so it is best to pass a list of the most important pages on the website with content such as "about us", "sustainability" and so on.
The video URL must be a YouTube link.

All the results will be written in a new folder inside outputs (/app/outputs in the container)


# References

[1] https://www.naveedafzal.com/posts/an-introduction-to-unsupervised-topic-segmentation-with-implementation/
