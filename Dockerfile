FROM python:3.10.5-slim-buster

WORKDIR /app

# Prevent pycache folder and files
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN set -ex \
    && apt-get update \
    && apt-get install -qq -y --no-install-recommends \
    curl \
    git \
    python3-dev \
    sudo \
    postgresql-client \
    libssl-dev \
    && pip install pipenv \
    && rm -rf /var/lib/apt/lists/* /usr/share/doc /usr/share/man \
    && apt-get clean

# Create appuser user for the application
RUN groupadd -g 9898 appuser && useradd --create-home -r -u 9898 -g appuser appuser -s /bin/bash
RUN usermod -aG sudo appuser
RUN mkdir /public_assets
RUN chown -R appuser:appuser /public_assets
RUN chown -R appuser:appuser /app
RUN chown -R appuser:appuser /etc/environment
RUN echo "appuser ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

ADD . ./

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

USER appuser

EXPOSE 8000

