from elasticsearch import Elasticsearch


ES_ARTICLE_INDEX = 'article'

ES_AUTHORS = [
    {
        "name": "Horse",
        "surname": "Rider",
        "photo_url": "https://www.horsetalk.co.nz/wp-content/uploads/2019/02/horse-riding-helmet-1.jpg"
    }
]

ES_ARTICLES = [
    {
        "id": 1,
        "title": "How to ride a horse",
        "category": "Horses",
        "content": "Riding a horse is not easy. You have to be careful not to fall off.",
        "author": ES_AUTHORS[0],
        "publish_date": "2020-01-01"
    },
    {
        "id": 2,
        "title": "How to ride a wild horse",
        "category": "Wild Horses",
        "content": "Yeehaw",
        "author": ES_AUTHORS[0],
        "publish_date": "1995-01-01"
    },
    {
        "id": 3,
        "title": "How to ride a horse 2",
        "category": "Horses",
        "content": "Riding a horse is very easy.",
        "author": ES_AUTHORS[0],
        "publish_date": "2020-01-02"
    },
    {
        "id": 4,
        "title": "How to ride a dog",
        "category": "Dogs",
        "content": "Riding a dog is not easy. You have to be careful not to fall off.",
        "author": ES_AUTHORS[0],
        "publish_date": "2020-01-03"
    }
]

REDIS_VIEWS = [

]

def insert_es_articles(es_client: Elasticsearch):
    if es_client.indices.exists(index=ES_ARTICLE_INDEX):
        es_client.indices.delete(index=ES_ARTICLE_INDEX)

    es_client.indices.create(index=ES_ARTICLE_INDEX)

    for article in ES_ARTICLES:
        es_client.index(index=ES_ARTICLE_INDEX, body=article)
