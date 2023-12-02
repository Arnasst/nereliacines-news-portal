from elasticsearch import Elasticsearch
from redis import Redis
from insert_data import ES_ARTICLE_INDEX, insert_es_articles

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

def main():
    es = Elasticsearch("http://localhost:9200")
    redis = Redis()

    # insert_es_articles(es)

    # articles = find_articles_by_content(es, "off")
    # print(articles)

    articles = find_articles_by_category(es, "Horses")
    print(articles)

if __name__ == "__main__":
    main()
