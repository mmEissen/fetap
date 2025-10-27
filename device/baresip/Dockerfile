# syntax=docker/dockerfile:1

# A very janky setup for cross compiling baresip for the rpi zero 2w:
# The dockerfile is split in such a way, that I can run the cmake configure steps on the
# rpi zero and all other steps on a github runner (check out the github workflow).
# The proper way to set this up would be to add a cmake cross compiling configuration
# as described here: https://cmake.org/cmake/help/book/mastering-cmake/chapter/Cross%20Compiling%20With%20CMake.html
# I However I am not sure how to configure everything correctly for the rpi zero 2w at the moment
# and this is a hacky workaround to figuring that out.
# It also assumes that there are no concurrent workflow runs, but that's not a problem since I'm the 
# only contributor anyway
FROM debian:latest AS step1

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


FROM mmeissen/fetap-baresip-prerequisites:step1 AS step2

RUN cd /re \
    && cmake -B build -DCMAKE_BUILD_TYPE=Release


FROM mmeissen/fetap-baresip-re-configured:step2 AS step3

RUN cd re \
    && cmake --build build -j \
    && cmake --install build \
    && ldconfig


FROM mmeissen/fetap-baresip-re-installed:step3 AS step4

RUN cd /baresip \
    && cmake -B build -DCMAKE_BUILD_TYPE=Release

FROM mmeissen/fetap-baresip-baresip-configured:step4 AS latest

RUN cd /baresip \
    && cmake --build build -j \
    && cmake --install build \
    && ldconfig

COPY config /config

ENTRYPOINT [ "baresip", "-f", "/" ]
