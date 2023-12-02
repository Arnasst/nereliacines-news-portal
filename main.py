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

def main():
    es = Elasticsearch("http://localhost:9200")
    redis = Redis()

    # insert_es_articles(es)

    articles = find_articles_by_content(es, "easy")
    print(articles)

if __name__ == "__main__":
    main()
