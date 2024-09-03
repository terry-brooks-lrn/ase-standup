FROM terrybrooks/dev-env:standup
LABEL Name="Gitpod Develpment Enviornment"
LABEL Version="1.0"

RUN apt-get update && apt-get install -y apt-transport-https ca-certificates curl gnupg && \
    curl -sLf --retry 3 --tlsv1.2 --proto "=https" 'https://packages.doppler.com/public/cli/gpg.DE2A7741A397C129.key' | gpg --dearmor -o /usr/share/keyrings/doppler-archive-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/doppler-archive-keyring.gpg] https://packages.doppler.com/public/cli/deb/debian any-version main" | tee /etc/apt/sources.list.d/doppler-cli.list && \
    apt-get update && \
    apt-get -y install doppler
    
EXPOSE 8000

COPY /workspace/ase-standup/.gitpod-entrypoint.sh /.gitpod-entrypoint.sh
ARG TOKEN
ENV DOPPLER_TOKEN=TOKEN
ENV DOPPLER_PROJECT=standup
ENV DOPPLER_CONFIG=dev


ENTRYPOINT ["doppler", "run", "--"]