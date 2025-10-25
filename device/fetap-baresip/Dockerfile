FROM fetap-baresip-conf:latest

RUN cd re \
    && cmake --build build -j \
    && cmake --install build \
    && ldconfig

RUN rm -rf re

RUN cd /baresip \
    && cmake --build build -j \
    && cmake --install build

ENTRYPOINT [ "baresip" ]
