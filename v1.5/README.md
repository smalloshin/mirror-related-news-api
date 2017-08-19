<h1> RELATED NEWS API v1.5 </h1> 

此為相關新聞API的說明文件。此文件包含了此套件的使用方法、API的設計邏輯以及技術細節。以下為目錄：

 * [1. API使用方法](#1)
     *   [1.1. 呼叫格式](#1.1)
     *   [1.2. 參數](#1.2)
 * [2. Docker啟動方式](#2)
     *   [2.1. 第一次啟動](#2.1) 
     *   [2,2. 啟動之後](#2.2)
 * [3. API邏輯與流程](#3)
     *   [3.1. offline](#3.1)
     *   [3.2. online](#3.2)
 * [4. 技術細節](#4)
     *   [4.1. 公用程式](#4.1)
     *   [4.2. 資料夾以及檔案](#4.2)

<h2 id=1> 1. API使用方法 </h2>
<h3 id=1.1>1.1. 呼叫格式</h3>

```sh
http://{api_host}:8080/related_news?{params_1}={value_1}&{param_2}={value_2}...
```
其中param_i為參數，value_i為其值。

<h3 id=1.2>1.2. 參數</h3>
 - id: 一個新聞文章的id
 - ids: 多個新聞文章的id
 - k: 顯示和上述id前k相關的新聞文章
 - debug: 指定為on時為，顯示代表新聞文章的詞以及其重要性

<h2 id=2>2. Docker啟動方法</h2>
<h3 id=2.1>2.1. 第一次啟動</h3>
本API主要的套件有**flask**、**anaconda**、**redis**。因此建議以docker方式啟動本API。必須要有執行docker之權限，啟動方法如下：
```sh
$ sudo bash api-start.sh
```
執行期間會執行2個動作，分別為：
 1. 啟動docker container，分別含有兩個api和cache service (flask以及redis)
 2. 將預設的資料放入快取(redis)中。

可在安裝的同一台機器下，利用同資料夾下的test_api.py測試其是否正確啟動。
```sh
$ python test_api.py
```
<h3 id=2.2>2.2. 啟動之後</h3>
啟動之後，docker container的名字為： mirror-related-news-api。目前雖然可以運行，但是資料仍為較舊的版本。建議啟動之後立即執行daily_batch.sh以建立所有運作所需之資料夾，並且維持資料維持在最新 (建模需要耗時較長時間)。
```sh
$ docker exec mirror-related-news-api bash daily_batch.sh
```

待執行完之後，請立即於背景執行營運用程式如下：
```sh
$ docker exec mirror-related-news-api python operation.sh
```

<h2 id=3>3. API流程及相關邏輯</h2>
此API之執行分成兩個部分，一個部分是offline計算最相關新聞，另一個部分是online回應api request。

<h3 id=3.1>3.1. Offline部份</h3>
 此部分共包含daily batch和micro batch兩個功能，由四個檔案所構成。其流程圖如下：
<img src="related-news-api-offline.png"/> 

 * get_raw_data.py
     * 輸入：[daily batch] 全部的新聞 ([micro batch]今天所有的新聞)
     * 輸出：所有新聞文章的json檔
 * extract_features.py
     * 輸入：所有新聞文章的json檔
     * 輸出：每個文章的{(重要斷詞i,TFIDF分數i)}
 * get_related_news.py
     * 輸入：[daily batch] 每個文章的{(重要斷詞i,TFIDF分數i)}  ([micro batch] daily batch產生的相關新聞、今天每個文章的{(重要斷詞i,TFIDF分數i)}
     * 輸出：每個文章的相關新聞
 * feed_to_redis.py
     * 輸入：每個文章的相關新聞
     * 輸出：Redis中的(key, value)-pair   (key = 新聞，value=相關新聞)
 
由於其流程類似，因此在程式中利用mode來控制每一個程式要以mode = batch (daily-batch)來執行還是以mode = recent (micro-batch)來執行。
 
<h3 id=3.2>3.2. Online部份</h3>
此部分由Flask和Redis構成。Flask為API server，而Redis儲存目前已經計算出結果的相關新聞列表。其sequence diagram如下：
<img src="related-news-api-online.png"/>

<h2 id=4>4. 技術細節</h2>
<h3 id=4.1>4.1. 公用程式</h3>
以下為使用者經常用到的公用程式：

 - **api-start.sh**
    為啟動API的檔案。用來啟動docker以及將初始資料放入快取中。啟動方法如上述，必須要有執行docker之權限。
 - **daily_batch.sh**
    利用目前所有新聞的文章做計算，求算出最相關文章。需要時間較長。
    ```sh
    $ bash daily_batch.sh
    ```
 - **operation.py**
    此檔案為在docker啟動後負責定期更新的檔案。初始設定為3分鐘執行一次micro batch以抓取今天的文章來算最相關新聞，每24小時執行一次daily batch以用網站上所有文章計算最相關新聞。以下為將其放入背景執行的方式：
    ```sh
    $ python operation.py &
    ```

<h3 id=4.2>4.2. 資料夾及目錄</h3>

 - **dict/** : 儲存字典檔的資料夾
     - moe.dict: 萌典字典檔 (新的專有名詞要加在此)
     - stopping_words.dict: 停止字的字典檔
 - **fallback/**：儲存預設資料檔案的資料夾     
 - **data/**：儲存所有新聞的json檔的資料夾
 - **recent/**：儲存今日目前所有新聞的json檔的資料夾
 - **output/**：儲存所有步驟產生的輸出的資料夾
     - *.msg: 儲存文章資訊以及TF-IDF資訊的DataFrame (pandas套件使用)
     - *.ann: 儲存求算相關新聞所需的Index (annoy套件使用) 
     - *.pkl: 程式產生的資料結構的Pickle  (cPickle套件使用)
