FROM debian:latest

RUN apt-get update &&  apt-get install -y \
    asterisk \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY pjsip.conf /etc/asterisk/pjsip.conf

ENTRYPOINT [ "asterisk", "-f" ]