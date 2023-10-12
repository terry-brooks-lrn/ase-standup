FROM ubuntu:22.04
RUN DEBIAN_FRONTEND=noninteractive \
  apt-get update \
  && apt-get install -y python3 \
  python-pip \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app/
RUN  cd /app
COPY ./requirements.txt /app/requirements.txt
COPY ./pyproject.toml /app/pyproject.toml
ENV POSTGRES_DB = standup_db
ENV POSTGRES_PASSWORD=learnosity
COPY ./standup /app/
RUN curl -sSL https://install.python-poetry.org | python3 -
COPY ./.docker-init.sh /app/init.sh
USER root
RUN chmod +x init.sh
RUN ./init.sh
EXPOSE 1995



ENTRYPOINT gunicorn standup.wsgi:application -b 127.0.0.1:1995
