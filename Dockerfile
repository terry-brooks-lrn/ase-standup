FROM ubuntu:22.04E
RUN
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
RUN poetry install

ENTRYPOINT [ "gunicorn" ]