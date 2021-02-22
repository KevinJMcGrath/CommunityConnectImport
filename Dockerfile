FROM python:3.9.2-alpine3.12

# RUN useradd -ms /bin/bash appuser
# USER appuser

MAINTAINER Kevin McGrath "kevin.mcgrath@symphony.com"

ADD requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

ADD . /app

CMD ["hypercorn", "-b", "0.0.0.0:8080", "main:app"]