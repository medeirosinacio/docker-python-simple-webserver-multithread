FROM python:2.7-slim
WORKDIR /app

# This hack is widely applied to avoid python printing issues in docker containers.
# See: https://github.com/Docker-Hub-frolvlad/docker-alpine-python3/pull/13
ENV PYTHONUNBUFFERED=1

COPY . .

# Update system e dependencies
RUN pip install --no-cache-dir --upgrade \
    pip \
    setuptools \
    && pip install --no-cache-dir -r requirements.txt

RUN rm -rf /app/logs/app.log && ln -sf /dev/stdout /app/logs/app.log

EXPOSE 60600

CMD [ "python", "/app/bin/webserver.py"]