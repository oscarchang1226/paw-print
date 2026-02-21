FROM astral/uv:python3.14-alpine3.23
LABEL authors="o_chang"

RUN apk add --no-cache \
    git \
    gnupg \
    pinentry \
    pinentry-tty \
    openssh-client

COPY docker/.profile /root/.profile

WORKDIR /app

CMD ["uv", "run", "manage.py", "runserver", "0.0.0.0:8080"]