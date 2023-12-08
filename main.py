import uuid
from elasticsearch import Elasticsearch
from redis import Redis, WatchError
from datetime import datetime, timedelta

from insert_data import ARTICLE_CATEGORIES, ES_ARTICLE_INDEX, insert_es_articles, insert_redis_articles

def find_articles_by_content(es_client: Elasticsearch, content: str):
    query = {
        "query": {
            "match": {
                "content": content
            }
        }
    }

    res = es_client.search(index=ES_ARTICLE_INDEX, body=query)
    return res["hits"]["hits"]

def find_articles_by_category(es_client: Elasticsearch, category: str, sort_by: str = "publish_date"):
    query = {
        "query": {
                "term": {
                    "category.keyword": category
            }
        },
        "sort": [
            {
                sort_by: {
                    "order": "desc"
                }
            }
        ]
    }

    res = es_client.search(index=ES_ARTICLE_INDEX, body=query)
    return res["hits"]["hits"]

def find_each_categories_two_latest_articles(es_client: Elasticsearch):
    query = {
        "size": 0,
        "aggs": {
            "categories": {
                "terms": {
                    "field": "category.keyword"
                },
                "aggs": {
                    "latest_articles": {
                        "top_hits": {
                            "size": 2,
                            "sort": [
                                {
                                    "publish_date": {
                                        "order": "desc"
                                    }
                                }
                            ]
                        }
                    }
                }
            }
        }
    }

    res = es_client.search(index=ES_ARTICLE_INDEX, body=query)
    return res["aggregations"]["categories"]["buckets"]

def find_articles_by_ids(es_client: Elasticsearch, ids: list):
    query = {
        "query": {
            "terms": {
                "id": ids
            }
        }
    }

    res = es_client.search(index=ES_ARTICLE_INDEX, body=query)
    return res["hits"]["hits"]

def find_five_most_popular_recent_articles(redis_client: Redis):
    twenty_four_hours_ago = datetime.now() - timedelta(hours=24)
    twenty_four_hours_ago = twenty_four_hours_ago.timestamp()

    recent_article_ids = redis_client.zrange("article:publish_dates", start=twenty_four_hours_ago, end="+inf", byscore=True, score_cast_func=float)

    recent_articles = None
    if recent_article_ids:
        suffix = uuid.uuid4()
        recent_articles = "recent_articles:" + str(suffix)
        redis_client.sadd(recent_articles, *recent_article_ids)
        redis_client.expire(recent_articles, 1000)
    if not recent_articles:
        return None

    with redis_client.pipeline() as pipe:
        pipe.watch("article:publish_dates")
        pipe.watch("article:views")
        pipe.multi()
        pipe.zinterstore("article:views:recent", ["article:views", recent_articles], aggregate="max")
        pipe.zrevrange("article:views:recent", 0, 4)
        pipe.delete(recent_articles)
        try:
            result = pipe.execute()
            return parse_to_int_list(result[1])
        except WatchError:
            print('Could not find five recent articles.')

def increment_article_views(redis_client: Redis, article_id: int):
    category = redis_client.hget(f"article:{article_id}", "category")
    category = category.decode("utf-8")

    with redis_client.pipeline() as pipe:
        pipe.watch(f"article:{article_id}")
        pipe.multi()
        pipe.hincrby(f"article:{article_id}", "views", 1)
        pipe.zincrby("article:views", 1, article_id)
        pipe.zincrby(f"article:{category}:views", 1, article_id)
        try:
            pipe.execute()
            return True
        except WatchError:
            print('Could not increment article views.')

def find_category_articles_sorted_by(redis_client: Redis, category: str, sort_by: str):
    if sort_by not in ["views", "publish_dates"]:
        raise ValueError("sort_by must be either 'views' or 'publish_dates'")
    if category not in ARTICLE_CATEGORIES:
        raise ValueError(f"Category must be one of {ARTICLE_CATEGORIES}")

    with redis_client.pipeline() as pipe:
        pipe.watch(f"article:{category}:{sort_by}")
        pipe.multi()
        pipe.zrevrange(f"article:{category}:{sort_by}", 0, -1)
        try:
            result = pipe.execute()
            return parse_to_int_list(result[0])
        except WatchError:
            print(f"Could not find category articles sorted by {sort_by}.")

def parse_to_int_list(list: list):
    if not list:
        return []
    return [int(item) for item in list]

def main():
    es = Elasticsearch("http://localhost:9200")
    redis = Redis(host='localhost', port=6379, db=0)

    # insert_es_articles(es)
    insert_redis_articles(redis)

    # articles = find_articles_by_content(es, "off")
    # print(articles)

    # articles = find_articles_by_category(es, "Horses")
    # print(articles)

    article_groups = find_each_categories_two_latest_articles(es)
    print(article_groups)

    article_ids = find_five_most_popular_recent_articles(redis)
    articles = find_articles_by_ids(es, article_ids)
    print(articles)

    result = increment_article_views(redis, 1)
    print(result)

    article_ids = find_category_articles_sorted_by(redis, ARTICLE_CATEGORIES[0], "views")
    print(article_ids)

    article_ids = find_category_articles_sorted_by(redis, ARTICLE_CATEGORIES[0], "publish_dates")
    print(article_ids)

if __name__ == "__main__":
    main()
