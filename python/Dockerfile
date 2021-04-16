
FROM ubuntu:18.04

ENV DEBIAN_FRONTEND=noninteractive

# Install some commands that are not included in the base image.
RUN apt-get update && apt-get install -y \
    python3-dev \
    git \
    python3-pip \
    wget \
    openssh-server \
    sudo
RUN pip3 install pipenv

RUN cd ~ &&\
    mkdir app

COPY . /app
WORKDIR /app

# Do not cache pip files.
# Setting the environment variable to false to disable pip cache_dir,
# although logic would say PIP_NO_CACHE_DIR=true means disable.
# https://pip.pypa.io/en/stable/user_guide/#configuration
# Update. This ambiguity has been fixed in PR 5884.
# https://github.com/pypa/pip/pull/5884/files
# Both true/false values in PIP_NO_CACHE_DIR would set the flag disabled.
# Once it's been released (likely in pip 19.0), we can fix this.
ENV PIP_NO_CACHE_DIR=false
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

# Install dependencies to system Python with --system,
# so that it doesn't need to run in a virtualenv.
RUN pipenv install

CMD ["/bin/bash", "-c", "tail -f /dev/null"]
