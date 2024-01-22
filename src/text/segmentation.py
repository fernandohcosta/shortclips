from itertools import chain, islice
import json

from gensim import corpora, models
import numpy as np
from sentence_transformers import SentenceTransformer
from scipy.signal import argrelmax
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MultiLabelBinarizer
import spacy


def delete_replicas(list_of_strings):
    idx = 1
    while idx < len(list_of_strings):
        if list_of_strings == list_of_strings[idx-1]:
            del list_of_strings[idx]
        idx += 1
    return list_of_strings


def get_threshold_segments(scores, threshold=0.1):
    segment_ids = np.where(scores >= threshold)[0]
    return segment_ids

def get_set_timestamps(segments, clusters):
    print(f"{len(segments) = }")
    print(f"{len(clusters) = }")
    cluster_idx = 0
    segment_idx = 0
    while segment_idx < len(segments) and cluster_idx < len(clusters):
        print(f"{len(clusters[cluster_idx]['text']) = }")
        print("clusters[cluster_idx]['text'][0] : ", clusters[cluster_idx]["text"][0])
        print("segments[segment_idx]['text'] : ", segments[segment_idx]['text'] )
        #if segments[segment_idx]["text"].strip() in clusters[cluster_idx]["text"][0]:
        if clusters[cluster_idx]["text"][0].strip().startswith(segments[segment_idx]["text"].strip()) or segments[segment_idx]["text"].strip().startswith(clusters[cluster_idx]["text"][0].strip()):
            clusters[cluster_idx]["start"] = segments[segment_idx]["start"]
            segment_idx +=1
            print(f"{segment_idx = }")
            print(f"{cluster_idx = }")
            while segment_idx < len(segments):
                print("clusters[cluster_idx]['text'][-1] : ", clusters[cluster_idx]["text"][-1])
                print("segments[segment_idx]['text'] : ", segments[segment_idx]['text'] )                
                #if segments[segment_idx]["text"].strip() in clusters[cluster_idx]["text"][-1]: 
                if clusters[cluster_idx]["text"][-1].strip().endswith(segments[segment_idx]["text"].strip()) or segments[segment_idx]["text"].strip().endswith(clusters[cluster_idx]["text"][-1].strip()): 
                    clusters[cluster_idx]["end"] = segments[segment_idx]["end"]
                    segment_idx +=1
                    cluster_idx +=1
                    print(f"{segment_idx = }")
                    print(f"{cluster_idx = }")
                    print()
                    break
                else:
                    segment_idx +=1
                    print(f"{segment_idx = }")
                    print(f"{cluster_idx = }")
        else:
            print("Error matching strings")
            break
        print("Next iteration")
    return clusters


def compute_threshold(scores):
    s = scores[np.nonzero(scores)]
    threshold = np.mean(s) - (np.std(s) / 2)
    # threshold = np.mean(s) - (np.std(s))
    return threshold


def get_depths(scores):
    depths = []
    for i in range(len(scores)):
        score = scores[i]
        l_peak = climb(scores, i, mode='left')
        r_peak = climb(scores, i, mode='right')
        depth = 0.5 * (l_peak + r_peak - (2*score))
        depths.append(depth)
    return np.array(depths)


def get_local_maxima(depth_scores, order=1):
    maxima_ids = argrelmax(depth_scores, order=order)[0]
    filtered_scores = np.zeros(len(depth_scores))
    filtered_scores[maxima_ids] = depth_scores[maxima_ids]
    return filtered_scores


def climb(seq, i, mode='left'):
    if mode == 'left':
        while True:
            curr = seq[i]
            if i == 0:
                return curr
            i = i-1
            if not seq[i] > curr:
                return curr
    if mode == 'right':
        while True:
            curr = seq[i]
            if i == (len(seq)-1):
                return curr
            i = i+1
            if not seq[i] > curr:
                return curr


def window(seq, n=3):
    it = iter(seq)
    result = tuple(islice(it, n))
    if len(result) == n: 
        yield result
    for elem in it:
        result = result[1:] + (elem,)
        yield result


def segment_transcription():
    with open('./outputs/segments.json', 'r') as f:
        segments = json.load(f)
    texts = ""
    for segment in segments:
        texts = texts + segment["text"]
    texts = [texts]
    print("texts: ", texts)
    #with open('./outputs/transcription.txt') as f:
    #    texts = f.read().splitlines()
    nlp = spacy.load('en_core_web_sm')
    sents = []
    for text in texts:
        doc = nlp(text)
        for sent in doc.sents:
            sents.append(sent)            
    MIN_LENGTH = 3
    tokenized_sents = [[token.lemma_.lower() for token in sent 
                        if not token.is_stop and 
                        not token.is_punct and token.text.strip() and 
                        len(token) >= MIN_LENGTH] 
                    for sent in sents]
    N_TOPICS = 5
    N_PASSES = 5
    dictionary = corpora.Dictionary(tokenized_sents)
    bow = [dictionary.doc2bow(sent) for sent in tokenized_sents]
    topic_model = models.LdaModel(corpus=bow, id2word=dictionary, 
                                num_topics=N_TOPICS, passes=N_PASSES)
    topic_model.show_topics()
    THRESHOLD = 0.05
    doc_topics = list(topic_model.get_document_topics(bow, minimum_probability=THRESHOLD))
    k = 3
    top_k_topics = [[t[0] for t in sorted(sent_topics, key=lambda x: x[1], reverse=True)][:k] 
                    for sent_topics in doc_topics]
    

    WINDOW_SIZE = 3
    window_topics = window(top_k_topics, n=WINDOW_SIZE)
    window_topics = [list(set(chain.from_iterable(window))) 
                    for window in window_topics]
    
    binarizer = MultiLabelBinarizer(classes=range(N_TOPICS))
    encoded_topic = binarizer.fit_transform(window_topics)
    
    coherence_scores = [cosine_similarity([pair[0]], [pair[1]])[0][0] 
                    for pair in zip(encoded_topic, encoded_topic[1:])]
    depth_scores = get_depths(coherence_scores)
    filtered_scores = get_local_maxima(depth_scores, order=1)
    threshold = compute_threshold(filtered_scores)
    segment_ids = get_threshold_segments(filtered_scores, threshold)
    segment_indices = segment_ids + WINDOW_SIZE
    segment_indices = [0] + segment_indices.tolist() + [len(sents)]
    slices = list(zip(segment_indices[:-1], segment_indices[1:]))

    segmented = [sents[s[0]: s[1]] for s in slices]
    clusters = {}
    for idx, current_cluster in enumerate(segmented):
        clusters[idx] = {"text": [i.text for i in current_cluster]}

    with open('./outputs/segments.json', 'r') as f:
        segments = json.load(f)

    print(clusters[0])
    print(segments[0]["start"])
    clusters = get_set_timestamps(segments, clusters)
    json_object = json.dumps(clusters, indent=4)
    with open("./outputs/clusters.json", "w") as outfile:
        outfile.write(json_object)
    return clusters


def segment_transcription_llm(run_folder):
    with open(run_folder / 'segments.json', 'r') as f:
        segments = json.load(f)
    texts = ""
    for segment in segments:
        texts = texts + segment["text"]
    texts = [texts]
    print("texts: ", texts)

    MODEL_STR = "sentence-transformers/all-mpnet-base-v2"
    model = SentenceTransformer(MODEL_STR)

    nlp = spacy.load('en_core_web_sm')
    sents = []
    #for text in texts:
    for segment in segments:
        doc = nlp(segment["text"].strip())
        for sent in doc.sents:
            #sents.append(sent)
            sents.append(segment)          

    WINDOW_SIZE = 3
    window_sent = list(window(sents, WINDOW_SIZE))
    window_sent = [' '.join([sent.text for sent in window]) for window in window_sent]
    encoded_sent = model.encode(window_sent)
    coherence_scores = [cosine_similarity([pair[0]], [pair[1]])[0][0] for pair in zip(encoded_sent, encoded_sent[1:])]

    depth_scores = get_depths(coherence_scores)
    filtered_scores = get_local_maxima(depth_scores, order=1)
    threshold = compute_threshold(filtered_scores)
    segment_ids = get_threshold_segments(filtered_scores, threshold)

    segment_indices = segment_ids + WINDOW_SIZE
    segment_indices = [0] + segment_indices.tolist() + [len(sents)]
    slices = list(zip(segment_indices[:-1], segment_indices[1:]))

    segmented = [sents[s[0]: s[1]] for s in slices]
    clusters = {}
    for idx, current_cluster in enumerate(segmented):
        clusters[idx] = {"text": [i.text for i in current_cluster]}

    print(clusters[0])
    print(segments[0]["start"])
    clusters = get_set_timestamps(segments, clusters)
    json_object = json.dumps(clusters, indent=4)
    with open(run_folder / "clusters.json", "w") as outfile:
        outfile.write(json_object)
    return clusters



def segment_transcription_llm_test(run_folder):
    with open(run_folder / 'segments.json', 'r') as f:
        segments = json.load(f)
    texts = ""
    for segment in segments:
        texts = texts + segment["text"]
    texts = [texts]
    print("texts: ", texts)

    MODEL_STR = "sentence-transformers/all-mpnet-base-v2"
    model = SentenceTransformer(MODEL_STR)

    nlp = spacy.load('en_core_web_sm')
    sents = []
    #for text in texts:
    for segment in segments:
        #doc = nlp(segment["text"].strip())
        #for sent in doc.sents:
            #sents.append(sent)
        sents.append(segment["text"].strip())          

    WINDOW_SIZE = 4
    window_sent = list(window(sents, WINDOW_SIZE))
    window_sent = [' '.join([sent for sent in window]) for window in window_sent]
    encoded_sent = model.encode(window_sent)
    coherence_scores = [cosine_similarity([pair[0]], [pair[1]])[0][0] for pair in zip(encoded_sent, encoded_sent[1:])]

    depth_scores = get_depths(coherence_scores)
    filtered_scores = get_local_maxima(depth_scores, order=1)
    threshold = compute_threshold(filtered_scores)
    segment_ids = get_threshold_segments(filtered_scores, threshold)

    segment_indices = segment_ids + WINDOW_SIZE
    segment_indices = [0] + segment_indices.tolist() + [len(sents)]
    slices = list(zip(segment_indices[:-1], segment_indices[1:]))

    segmented = [sents[s[0]: s[1]] for s in slices]
    clusters = {}
    for idx, current_cluster in enumerate(segmented):
        clusters[idx] = {"text": [i for i in current_cluster]}

    print(clusters[0])
    print(segments[0]["start"])

    for cluster in clusters:
        clusters[cluster]["text"] = delete_replicas(clusters[cluster]["text"])

    clusters = get_set_timestamps(segments, clusters)

    json_object = json.dumps(clusters, indent=4)
    with open(run_folder / "clusters.json", "w") as outfile:
        outfile.write(json_object)
    return clusters