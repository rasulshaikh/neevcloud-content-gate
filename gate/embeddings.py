"""Vector index over the published corpus.

Prototype uses TF-IDF + cosine similarity: zero external services, runs
anywhere. Production swaps this class for semantic embeddings (Voyage or
text-embedding-3) stored in pgvector. The interface stays the same, which
is the point: checks do not care what produces the vectors.
"""

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class CorpusIndex:
    def __init__(self, posts):
        self.posts = posts
        self.vectorizer = TfidfVectorizer(
            stop_words="english", ngram_range=(1, 2), max_features=20000
        )
        texts = [p.title + "\n" + p.body for p in posts]
        if texts:
            self.matrix = self.vectorizer.fit_transform(texts)
        else:
            self.matrix = None

    def similarities(self, post):
        """Cosine similarity of `post` against every published post."""
        if self.matrix is None:
            return []
        vec = self.vectorizer.transform([post.title + "\n" + post.body])
        sims = cosine_similarity(vec, self.matrix)[0]
        ranked = sorted(
            zip(self.posts, sims), key=lambda t: t[1], reverse=True
        )
        return [(p, float(s)) for p, s in ranked]
