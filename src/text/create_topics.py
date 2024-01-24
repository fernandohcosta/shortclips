import json
from top2vec import Top2Vec


def create_topics(run_folder):

    with open(run_folder / "clusters.json", "r") as f:
        clusters = json.load(f)

    with open(run_folder / "site_texts.json", "r") as f:
        topics = json.load(f)

    corpus_clusters = [clusters[i]["text"][0] for i in clusters]
    corpus_website = [topics[i][0] for i in topics]
    corpus = [*corpus_clusters, *corpus_website]
    print(corpus)

    model = Top2Vec(documents=corpus*10, speed="learn", embedding_model='distiluse-base-multilingual-cased', workers=8)
    model.save("trained_top2vec")
    n_topics = model.get_num_topics()
    print(f"{n_topics = }")
    for i in range(n_topics):
        print(i)
        topic_words, word_scores, topic_nums = model.get_topics(i)
        print(topic_words[:5])
        print()
    return