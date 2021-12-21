FROM python:3.9

ENV WHITELIST ${WHITELIST}
ENV WHITELIST_UPLOAD ${WHITELIST_UPLOAD}

RUN \
 apt-get update -y && \
 apt-get install -y iproute2

# Create app directory
WORKDIR /app

# Install app dependencies
COPY . /app

RUN pip install \
    -U pip setuptools \
    -r requirements.txt

EXPOSE 8080

CMD /bin/s -c source docker-helpers/whitelist-host-ips \
    python taricapi.py
