ARG BUILD_FROM
FROM $BUILD_FROM
WORKDIR /app
RUN apk add --no-cache python3 py3-pip
COPY app /app
RUN pip3 install --no-cache-dir --break-system-packages \
    quarry \
    paho-mqtt \
    requests \
    aiohttp
COPY run.sh /
RUN chmod a+x /run.sh
ENV PYTHONPATH=/app
CMD [ "/run.sh" ]
