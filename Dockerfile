# base image
FROM python:3.10-slim-bookworm AS base

# production stage
FROM base AS production

EXPOSE 5556

# set timezone
ENV TZ=UTC

WORKDIR /magic-doc

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc g++ libc-dev libffi-dev libgmp-dev libmpfr-dev libmpc-dev libreoffice

# Copy source code
COPY . /magic-doc
RUN pip install '.[cpu]' --extra-index-url https://wheels.myhloli.com

ENTRYPOINT ["/bin/bash", "-c", "cd magic_doc/restful_api && python3 app.py >>out.log 2>&1"]