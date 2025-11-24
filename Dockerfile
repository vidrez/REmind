# Use an official Python runtime as a parent image
FROM python:3.14-slim

WORKDIR /flask_website
COPY . /flask_website

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get -y install gcc && \
    apt-get -y install graphviz libgraphviz-dev pkg-config mariadb-server && \
    rm -rf /var/lib/apt/lists/*

RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 4000

WORKDIR /flask_website/re-webui

# Run app.py when the container launches
CMD ["flask", "run", "--host", "0.0.0.0", "-p", "4000"]

