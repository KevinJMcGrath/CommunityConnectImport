FROM python:3.9.2-slim-buster

MAINTAINER Kevin McGrath "kevin.mcgrath@symphony.com"

ADD requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

ADD . /app

RUN useradd -ms /bin/bash appuser
USER appuser

CMD ["hypercorn", "-b", "0.0.0.0:8080", "app/main:app"]