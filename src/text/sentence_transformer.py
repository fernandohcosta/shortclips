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

    #topics_embeddings = [get_embedding(topics[topic]) for topic in topics]
    topics_embeddings = [get_embedding(" ".join([topic, topics[topic][0]])) for topic in topics]
    #print(f"{len(topics_embeddings) = }")
    #print(f"{topics_embeddings[0].shape = }")
    topic_names = [topic for topic in topics] 
    #print(f"{topic_names}")
    for cidx, cluster in enumerate(clusters):
        joined_text = ' '.join(clusters[cluster]["text"])
        cluster_embedding = get_embedding(joined_text)
        #print(f"{cluster_embedding.shape = }")
        similarities = [util.cos_sim(cluster_embedding, topic_embedding)[0] for topic_embedding in topics_embeddings]
        similarities = torch.stack(similarities)
        #print(similarities)
        max_idx = torch.argmax(similarities).item() #max(enumerate(similarities), key=lambda x: x[1])
        #print(f"{max_idx = }")
        #print(f"{type(max_idx)}")
        clusters[str(cidx)]["topic"] = topic_names[max_idx]
        clusters[str(cidx)]["topic_similarity"] = similarities[max_idx].item()
    
    json_object = json.dumps(clusters, indent=4)
    with open(run_folder / "clusters.json", "w") as outfile:
        outfile.write(json_object)

