FROM debian:latest

RUN apt-get update &&  apt-get install -y \
    curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN curl -O https://github.com/mmEissen/asterisk/releases/download/v0.1.1/asterisk && chmod +x asterisk

COPY pjsip.conf /etc/asterisk/pjsip.conf

ENTRYPOINT [ "./asterisk", "-f" ]