#!/bin/bash
echo "***** BUILD DOCKER IMAGES *****"
docker-compose up --build -d
echo "***** LOAD DEFAULT DATA *****"
docker exec mirror-related-news-api python feed_to_redis.py
