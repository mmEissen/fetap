FROM debian:latest

RUN apt-get update &&  apt-get install -y \
    build-essential \
    curl \
    unzip

RUN curl -o asterisk.zip -L https://github.com/asterisk/asterisk/archive/refs/tags/certified-20.7-cert7.zip
RUN unzip asterisk.zip
WORKDIR /asterisk-certified-20.7-cert7

RUN ./contrib/scripts/install_prereq install
RUN ./configure
RUN make
RUN make install

WORKDIR /
RUN rm -rf /asterisk-certified-20.7-cert7

COPY pjsip.conf /etc/asterisk/pjsip.conf

ENTRYPOINT [ "asterisk", "-f" ]