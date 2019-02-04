FROM egeneralov/tkh
RUN apt-get update -q && \
    apt-get install -yq python3-pip && \
    apt-get autoclean -yq && \
    apt-get clean -yq

WORKDIR /app
ADD requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
ADD . .
CMD gunicorn --bind 0.0.0.0:8080 --workers 8 app:app
