FROM python:3.9

# Create app directory
WORKDIR /app

# Install app dependencies
COPY . /app

RUN pip install \
    -U pip setuptools \
    -r requirements.txt

EXPOSE 8080
CMD [ "python", "taricapi.py" ]
