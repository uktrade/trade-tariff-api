FROM python:3.9

ENV WHITELIST ${WHITELIST}
ENV WHITELIST_UPLOAD ${WHITELIST_UPLOAD}

RUN \
 apt-get update -y && \
 apt-get install -y iproute2

# Create app directory
WORKDIR /app

# Install Python package dependencies.
COPY requirements*.txt /app/
RUN pip install --upgrade pip setuptools
RUN pip install -r requirements.txt --no-warn-script-location

# Copy app source code.
COPY . /app

EXPOSE 8080
CMD /bin/s -c source docker-helpers/whitelist-host-ips \
    python taricapi.py
