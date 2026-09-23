import os

from dotenv import load_dotenv
from openai import OpenAI
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key) if api_key else None


def calculate_semantic_scores(
    descriptions: list[str],
    preferences: str,
) -> list[float]:

    if not descriptions:
        return []

    if client is not None:
        try:
            texts = [preferences] + descriptions

            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=texts,
            )

            embeddings = [
                item.embedding
                for item in response.data
            ]

            preference_embedding = embeddings[0]
            description_embeddings = embeddings[1:]

            similarities = cosine_similarity(
                [preference_embedding],
                description_embeddings,
            )[0]

            return similarities.tolist()

        except Exception as error:
            print(f"OpenAI embeddings failed: {error}")
            print("Falling back to TF-IDF")

    return calculate_tfidf_scores(
        descriptions,
        preferences,
    )


def calculate_tfidf_scores(
    descriptions: list[str],
    preferences: str,
) -> list[float]:

    texts = [preferences] + descriptions

    vectorizer = TfidfVectorizer(
        lowercase=True,
    )

    vectors = vectorizer.fit_transform(texts)

    preference_vector = vectors[0]
    description_vectors = vectors[1:]

    similarities = cosine_similarity(
        preference_vector,
        description_vectors,
    )[0]

    return similarities.tolist()