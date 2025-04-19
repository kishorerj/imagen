# I followed this to create vectior search index https://colab.sandbox.google.com/github/GoogleCloudPlatform/generative-ai/blob/main/embeddings/hybrid-search.ipynb#scrollTo=yyYrclP5pYWR
from google.cloud.aiplatform.matching_engine.matching_engine_index_endpoint import (
    HybridQuery,
)
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from vertexai.preview.language_models import TextEmbeddingModel
from google.cloud import aiplatform

import pandas as pd

CSV_URL = "https://raw.githubusercontent.com/GoogleCloudPlatform/generative-ai/main/gemini/sample-apps/photo-discovery/ag-web/google_merch_shop_items.csv"

# Load the CSV file into a DataFrame
# df = pd.read_csv(CSV_URL)
# df["title"]

aiplatform.init(project='kishorejoonix1', location='us-central1')

model = TextEmbeddingModel.from_pretrained("text-embedding-005")


# wrapper
def get_dense_embedding(text):
    return model.get_embeddings([text])[0].values


# test it
get_dense_embedding("Chrome Dino Pin")

# Initialize TfidfVectorizer
vectorizer = TfidfVectorizer()

def get_sparse_embedding(text):
    # Transform Text into TF-IDF Sparse Vector
    tfidf_vector = vectorizer.transform([text])

    # Create Sparse Embedding for the New Text
    values = []
    dims = []
    for i, tfidf_value in enumerate(tfidf_vector.data):
        values.append(float(tfidf_value))
        dims.append(int(tfidf_vector.indices[i]))
    return {"values": values, "dimensions": dims}




query_text = "Kids"
query_dense_emb = get_dense_embedding(query_text)
query_sparse_emb = get_sparse_embedding(query_text)
query = HybridQuery(
    dense_embedding=query_dense_emb,
    sparse_embedding_dimensions=query_sparse_emb["dimensions"],
    sparse_embedding_values=query_sparse_emb["values"],
    rrf_ranking_alpha=0.5,
)
UID='04181118'
#point to the vector search endpoint

DEPLOYED_HYBRID_INDEX_ID = f"vs_hybridsearch_deployed_{UID}"
my_index_endpoint = aiplatform.MatchingEngineIndexEndpoint.create(
    display_name=f"vs-hybridsearch-index-endpoint-{UID}", public_endpoint_enabled=True
)

response = my_index_endpoint.find_neighbors(
    deployed_index_id=DEPLOYED_HYBRID_INDEX_ID,
    queries=[query],
    num_neighbors=10,
)

# print results
for idx, neighbor in enumerate(response[0]):
    title = 'abc'#df.title[int(neighbor.id)]
    dense_dist = neighbor.distance if neighbor.distance else 0.0
    sparse_dist = neighbor.sparse_distance if neighbor.sparse_distance else 0.0
    print(f"{title:<40}: dense_dist: {dense_dist:.3f}, sparse_dist: {sparse_dist:.3f}")
