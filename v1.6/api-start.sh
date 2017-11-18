#!/bin/bash
echo "***** BUILD DOCKER IMAGES *****"
sudo docker-compose up --build -d
echo "***** LOAD DEFAULT DATA *****"
sudo docker exec mirror-related-news-api python feed_to_redis.py
echo "Finished!"
