FROM python:3.9.12-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_DIR=/app
ENV PYTHONPATH=$PYTHONPATH:$APP_DIR

COPY requirements.txt ./
RUN apt-get update


RUN pip install -U --user pip && pip install --user -r requirements.txt

WORKDIR ${APP_DIR}
CMD [ "python", "main.py" ]
EXPOSE 5000