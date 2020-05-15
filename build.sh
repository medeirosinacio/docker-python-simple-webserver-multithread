#!/usr/bin/env bash

if [[ "$(docker images -q sshcon 2>/dev/null)" == "" ]]; then
    docker build -t sshcon --network=host --force-rm .
fi

docker run --restart=always -d -p 60600:60600 -v "$PWD":/app sshcon
