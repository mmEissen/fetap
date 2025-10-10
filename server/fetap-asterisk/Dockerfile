FROM debian:latest

RUN apt-get update &&  apt-get install -y \
    build-essential \
    gcc \
    g++ \
    make \
    curl \
    unzip

RUN curl -o asterisk.zip -L https://github.com/asterisk/asterisk/archive/refs/tags/certified-20.7-cert7.zip
RUN unzip asterisk.zip && rm -f asterisk.zip
WORKDIR /asterisk-certified-20.7-cert7

RUN ./contrib/scripts/install_prereq install
ENV CFLAGS="-O2 -mcpu=cortex-a72"
ENV CXXFLAGS="$CFLAGS"
ENV LDFLAGS=""
RUN ./configure
RUN make
RUN make install

WORKDIR /
RUN rm -rf /asterisk-certified-20.7-cert7

COPY conf /etc/asterisk

ENTRYPOINT [ "asterisk", "-f" ]