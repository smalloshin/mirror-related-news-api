!#/bin/bash
echo "**** [Step 1] Clean old data and prepare directories ****"
rm -rf data
mkdir data
mkdir output
echo "Done!"
echo "**** [Step 2] Crawl news articles ****"
python get_raw_data.py
echo "**** [Step 3] Compute features for each news articles ****"
python extract_features.py
echo "**** [Step 4] Compute the related news ****"
echo "(may take long time)"
python get_related_news.py
echo "Done!"
echo "**** [Step 5] Loading data to Redis ****"
python feed_to_redis.py
