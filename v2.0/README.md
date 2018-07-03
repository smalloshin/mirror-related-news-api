# Related News Engine V2.0

## 本次改版概要
- 修正前一版錯誤
- 移除API部分
- 移除fallback logic
- 利用PubSub進行對新進的新聞文章進行收集
- Index方法改成Facebook PySparnn，以增快批次處理、新進文章處理速度
- 改變新進文章處理邏輯
- Redis不用字典儲存，直接用related-news-v2-{news_id} --> news_json
- 爬蟲部分改用multiprocess增快速度

## 主要需要套件
- 爬蟲與解析用套件
  1. urllib, urllib2
  1. BeautifulSoup
- 分析用套件
  1. jieba
  1. sklearn
  1. pandas
  1. pysparnn (https://github.com/facebookresearch/pysparnn)
- 資料庫套件
   1. redis
- Message Queue
  1. google.cloud.pubsub_v1

## 使用方法
- 批次處理
每天執行一次的工作，將會利用全部的新聞重新計算一次相關新聞列表
```sh
$ python DailyOperation.py
```
- 即時處理
執行之後，將會從PubSub的Message Queue中讀取即時來的新聞，產生這些即時來的新聞的相關新聞列表。若沒有手動停止，則此程式會一直監聽是否新的新聞產生，以便及時處理。
```sh
$ python GetPubSubStreaming.py
```

## 程式邏輯
此程式主要分成兩個部分。一個部分是爬蟲的部分，另外一個部分是相關新聞的核心。爬蟲中分成批次和即時兩個檔案，而核心部分可以設定mode='batch'來執行批次分析以及mode='pubsub'來進行即時的分析。最後結果將會寫到redis中。
![Related News Engine V2](https://imgur.com/qwuCiSP)

## 檔案結構與程式功用
### 資料夾
- dict/ : 存放字典檔
  - 萌典解析後的字典檔: moe.dict
  - 停止字的字典: stopping_words.dict
- data/ : 存放批次處理時抓取下的原始檔案
  - 檔案名稱為news-page-XXX，是json格式
- streaming-data/ : 存放PubSub抓下的原始檔案
  - 檔案名稱為streaming-{建立檔案的時間}，(如streaming-200832）
- intermediate-results/ : 存放程式產生的中間結果
  - news-id-tfidf50-topic-category.msg: 將新聞內容彙整成的DataFrame
  - cv.pkl: 新聞的向量
  - id_list.pkl: 新聞的id
  - pysparnn-index.pkl: 將新聞表示成的向量的index
  - related-news-pysparnn-{建立檔案的時間}.result: 相關新聞的id列表
- credentials/ : 存放PubSub所要用的憑證 (可以在related-news-engine.conf更改路徑)

### 程式功用
  - CrawlRawJson.py: 利用API抓取新聞文章原始json檔
  - ExtractTDIDF.py: 將原始json檔中的新聞文章內容算出代表新聞文章的單字及tfidf分數
  - GetFeatureVectors.py: 將文章表示成tfidf-vectors
  - BuildIndexTreeV2.py: 將tfidf-vectors建立成index (用pysparnn套件)，並且求出相關新聞
  - FeedToRedisV2.py: 將相關新聞的結果放入Redis
  - related-news-engine.conf: 設定檔
### 輸出格式
輸出到Redis中的為key-value pair，其格式為：
  - key: related-news-v2-{news_id}
  - value: news_id的相關新聞的json string，用json.loads()後為字典格式

