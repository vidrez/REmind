# Use an official Python runtime as a parent image
FROM python:3.14-slim

WORKDIR /flask_website
COPY ./re-webui /flask_website
COPY requirements.txt /flask_website/requirements.txt

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get -y install gcc && \
    apt-get -y install graphviz libgraphviz-dev pkg-config mariadb-server && \
    rm -rf /var/lib/apt/lists/*

RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 4000

RUN rm requirements.txt
WORKDIR /

CMD ["python", "-m", "flask_website.flask_website"]

