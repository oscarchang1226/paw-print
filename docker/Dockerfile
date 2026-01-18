FROM astral/uv:python3.14-alpine3.23
LABEL authors="o_chang"

RUN apk add gnupg pinentry pinentry-tty

CMD ["uv", "run", "manage.py", "runserver", "0.0.0.0:8080"]