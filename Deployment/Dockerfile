FROM python:3.10-slim

WORKDIR /app

COPY  ./app/ ./

RUN apt-get update && \
    apt-get install -y ffmpeg && \
    pip install flask && \
    pip install psycopg2-binary && \
    pip install requests && \
    pip install flasgger && \
    pip install google-api-python-client && \
    pip install youtube-comment-downloader && \
    pip install pandas && \
    pip install nltk && \
    pip install emoji && \
    pip install joblib

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
