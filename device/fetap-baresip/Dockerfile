# syntax=docker/dockerfile:1
FROM debian:latest AS prerequisites

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
    && mv re-4.1.0 re \
    && rm libre.zip

RUN curl -Lso baresip.zip https://github.com/baresip/baresip/archive/refs/tags/v4.1.0.zip \
    && unzip baresip.zip \
    && mv baresip-4.1.0 baresip \
    && rm baresip.zip


FROM mmeissen/fetap-baresip-prerequisites:latest AS re-configured

RUN cd /re \
    && cmake -B build -DCMAKE_BUILD_TYPE=Release


FROM mmeissen/fetap-baresip-re-configured:latest AS re-installed

RUN cd re \
    && cmake --build build -j \
    && cmake --install build \
    && ldconfig


FROM mmeissen/fetap-baresip-re-installed:latest AS baresip-configured

RUN cd /baresip \
    && cmake -B build -DCMAKE_BUILD_TYPE=Release

FROM mmeissen/fetap-baresip-baresip-configured:latest AS final

RUN cd /baresip \
    && cmake --build build -j \
    && cmake --install build

ENTRYPOINT [ "baresip" ]