#!/bin/bash
if [ $1 = True ]; then
    echo "Execution for the first time"
fi

echo "**** [Step 1] Prepare directories ****"
mkdir data
mkdir output
echo "Done!"
echo "**** [Step 2] Crawl news articles ****"
python get_raw_data.py
echo "**** [Step 3] Compute features for each news articles ****"
if [ $1 = True ]; then
    python extract_features.py True
else
    python extract_features.py False
fi

echo "**** [Step 4] Compute the related news ****"
echo "(may take long time)"
python get_related_news.py
echo "Done!"
echo "**** [Step 5] Loading data to Redis ****"
python feed_to_redis.py
