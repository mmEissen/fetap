FROM debian:latest

RUN apt-get update &&  apt-get install -y --no-install-recommends \
    make \
    cmake \
    pkg-config \
    git \
    clang \
    ca-certificates \
    libopus-dev \
    libasound2-dev \
    libmosquitto-dev \
    libspandsp-dev \
    libpulse-dev \
    libssl-dev \
    libz-dev \
    curl \
    unzip

RUN curl -Lso libre.zip https://github.com/baresip/re/archive/refs/tags/v4.1.0.zip \
    && unzip libre.zip \
    && rm libre.zip

RUN cd re-4.1.0 \
    && cmake -B build -DCMAKE_BUILD_TYPE=Release \
    && cmake --build build -j \
    && cmake --install build \
    && ldconfig

RUN rm -rf re-4.1.0

RUN curl -Lso baresip.zip https://github.com/baresip/baresip/archive/refs/tags/v4.1.0.zip \
    && unzip baresip.zip \
    && rm baresip.zip

WORKDIR /baresip-4.1.0
RUN cmake -B build -DCMAKE_BUILD_TYPE=Release \
    && cmake --build build -j \
    && cmake --install build

ENTRYPOINT [ "baresip" ]
