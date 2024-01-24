import json
import requests
import io
import bs4
from time import sleep
import numpy as np


def get_page_links(url):
    """
    Finds all links within the given url using the <a> tag
    """
    html = requests.get(url).content
    soup = bs4.BeautifulSoup(html, "html.parser")
    links = [a["href"] for a in soup.find_all("a", href=True)]
    filtered_links = []
    for link in links:
        if link.startswith(url) and link.count('/') < 5:
            filtered_links.append(link)
    return filtered_links

def get_title_text(url):
    html = requests.get(url,
                            headers={'User-Agent': 'Mozilla/5.0','cache-control': 'max-age=0'}, cookies={'cookies':''})
    soup = bs4.BeautifulSoup(html.text, 'html.parser')
    title_text = {}
    for header in soup.find_all(['h1', 'h2', 'h3']):
        current_title = header.get_text()
        title_text[current_title.strip()] = []
        for elem in header.next_siblings:
            if elem.name and elem.name.startswith('h'):
                break
            if elem.name == 'p':
                current_text = elem.get_text()
                if current_text.strip() and current_title.strip():
                    title_text[current_title.strip()].append(current_text.strip())
    to_remove = []
    for key in title_text:
        if not key or not len(title_text[key]) > 0:
            to_remove.append(key)
    [title_text.pop(key, None) for key in to_remove]

    return title_text

def get_website_texts(url, run_folder):
    if type(url) is list:
        links = url
    else:
        links = get_page_links(url)
        sleep(np.random.randint(5, 15))
    
    complete_topics = {}
    for n, link in enumerate(links):
        complete_topics.update(get_title_text(link))
        sleep(np.random.randint(5, 15))

    json_object = json.dumps(complete_topics, indent=4)
    with open(run_folder / "site_texts.json", "w") as outfile:
        outfile.write(json_object)