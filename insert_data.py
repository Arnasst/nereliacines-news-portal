from datetime import datetime, timedelta
from elasticsearch import Elasticsearch
from redis import Redis

ARTICLE_CATEGORIES = ["horses", "wild_horses", "dogs"]

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
        "category": ARTICLE_CATEGORIES[0],
        "content": "Riding a horse is not easy. You have to be careful not to fall off.",
        "author": ES_AUTHORS[0],
        "publish_date": (datetime.now() - timedelta(days=1)).timestamp()
    },
    {
        "id": 2,
        "title": "How to ride a wild horse",
        "category": ARTICLE_CATEGORIES[1],
        "content": "Yeehaw",
        "author": ES_AUTHORS[0],
        "publish_date": (datetime.now() - timedelta(hours=2)).timestamp()
    },
    {
        "id": 3,
        "title": "How to ride a horse 2",
        "category": ARTICLE_CATEGORIES[0],
        "content": "Riding a horse is very easy.",
        "author": ES_AUTHORS[0],
        "publish_date": (datetime.now() - timedelta(hours=3)).timestamp()
    },
    {
        "id": 4,
        "title": "How to ride a dog",
        "category": ARTICLE_CATEGORIES[2],
        "content": "Riding a dog is not easy. You have to be careful not to fall off.",
        "author": ES_AUTHORS[0],
        "publish_date": (datetime.now() - timedelta(days=5)).timestamp()
    }
]

def insert_es_articles(es_client: Elasticsearch):
    if es_client.indices.exists(index=ES_ARTICLE_INDEX):
        es_client.indices.delete(index=ES_ARTICLE_INDEX)

    es_client.indices.create(index=ES_ARTICLE_INDEX)

    for article in ES_ARTICLES:
        es_client.index(index=ES_ARTICLE_INDEX, body=article)

def insert_redis_articles(redis_client: Redis):
    redis_client.flushall()

    for article in ES_ARTICLES:
        redis_client.hset(f"article:{article['id']}", mapping={"category": article["category"], "views": 0})
        redis_client.zadd(f"article:{article['category']}:views", {article["id"]: 0})
        redis_client.zadd(f"article:{article['category']}:publish_dates", {article["id"]: article["publish_date"]})
        redis_client.zadd(f"article:publish_dates", {article["id"]: article["publish_date"]})
        redis_client.zadd(f"article:views", {article["id"]: 0})
