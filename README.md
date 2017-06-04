# mirror-related-news-api

* requirements
  * flask
  * redis
  * anaconda
  * jieba
  * annoy

* Scripts
  * Start the api: api-start.sh
  * Daily maintenance: daily_batch.sh
  
* Usage
  * http://{api_host}:5000/related_news?k={number of related news for ids}&ids={id1},{id2}&debug={on or off}
