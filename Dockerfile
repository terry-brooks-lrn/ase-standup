FROM ubuntu:22.04
RUN DEBIAN_FRONTEND=noninteractive \
  apt-get update \
  && apt-get install -y python3 \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app/
RUN  cd /app
COPY .requirements.txt /app/requirements.txt
COPY .pyproject.toml /app/pyproject.toml
COPY . /app/
RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN ./init.sh
EXPOSE 1995



ENTRYPOINT gunicorn standup.wsgi:application -b 127.0.0.1:1995
