FROM python:3.6-alpine AS base

FROM base AS build
WORKDIR /app
RUN apk --update add \
    build-base \
    git \
    libffi-dev \
    libxml2-dev \
    libxslt-dev \
    linux-headers \
    musl-dev \
    openssl-dev
RUN git clone https://github.com/StarlitGhost/FediRun.git /app
RUN pip install --no-cache-dir -r requirements.txt

FROM base
RUN apk add libffi libxml2 libxslt musl openssl
COPY --from=build /usr/local /usr/local
COPY --from=build /app /app
WORKDIR /app
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ananas config/config.cfg
