import json

from sentence_transformers import SentenceTransformer, util
import torch


def get_embedding(sentences):
    model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
    embeddings = model.encode(sentences)
    return embeddings


def define_topic(run_folder):

    with open(run_folder / "clusters.json", "r") as f:
        clusters = json.load(f)

    with open(run_folder / "site_texts.json", "r") as f:
        topics = json.load(f)

    topics_embeddings = [get_embedding(" ".join([topic, topics[topic][0]])) for topic in topics]
    topic_names = [topic for topic in topics] 

    for cidx, cluster in enumerate(clusters):
        joined_text = ' '.join(clusters[cluster]["text"])
        cluster_embedding = get_embedding(joined_text)
        similarities = [util.cos_sim(cluster_embedding, topic_embedding)[0] for topic_embedding in topics_embeddings]
        similarities = torch.stack(similarities)
        max_idx = torch.argmax(similarities).item()
        clusters[str(cidx)]["topic"] = topic_names[max_idx]
        clusters[str(cidx)]["topic_similarity"] = similarities[max_idx].item()
    
    json_object = json.dumps(clusters, indent=4)
    with open(run_folder / "clusters.json", "w") as outfile:
        outfile.write(json_object)

