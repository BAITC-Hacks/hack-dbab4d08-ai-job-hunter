import os

from dotenv import load_dotenv
from openai import OpenAI
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key) if api_key else None

MODEL = "text-embedding-3-small"

# Кэш embeddings описаний подрядчиков
description_cache: dict[str, list[float]] = {}


def get_embeddings(texts: list[str]) -> list[list[float]]:
    response = client.embeddings.create(
        model=MODEL,
        input=texts,
    )

    return [
        item.embedding
        for item in response.data
    ]


def calculate_semantic_scores(
    descriptions: list[str],
    preferences: str,
) -> list[float]:

    if not descriptions:
        return []

    if client is not None:
        try:
            # Находим описания, embeddings которых ещё нет
            missing_descriptions = list(
                dict.fromkeys(
                    description
                    for description in descriptions
                    if description not in description_cache
                )
            )

            # Один batch-запрос для новых описаний
            if missing_descriptions:
                embeddings = get_embeddings(
                    missing_descriptions
                )

                for description, embedding in zip(
                    missing_descriptions,
                    embeddings,
                ):
                    description_cache[description] = embedding

            # Для пользовательского пожелания embedding
            preference_embedding = get_embeddings(
                [preferences]
            )[0]

            # Embeddings подрядчиков уже берём из кэша
            description_embeddings = [
                description_cache[description]
                for description in descriptions
            ]

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