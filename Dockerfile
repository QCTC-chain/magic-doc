# base image
FROM python:3.10-slim-bookworm

# set timezone
ENV TZ=UTC

RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update \
    && apt-get install -y --no-install-recommends gcc g++ libc-dev libffi-dev libgmp-dev libmpfr-dev libmpc-dev libreoffice libgl1

WORKDIR /magic-doc

# Copy source code
COPY . /magic-doc

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install '.[gpu]' --extra-index-url https://wheels.myhloli.com

EXPOSE 5556

ENTRYPOINT ["/bin/bash", "-c", "python3 magic_doc/restful_api/app.py"]