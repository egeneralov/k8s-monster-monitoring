FROM egeneralov/tkh
RUN apt-get update -q && \
    apt-get install -yq python3-pip && \
    apt-get autoclean -yq && \
    apt-get clean -yq

WORKDIR /app
ADD requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
ADD . .
CMD python3 /app/app.py
