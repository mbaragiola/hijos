FROM python:3.7.2-alpine3.9

ENV PYTHONUNBUFFERED 1

RUN apk update \
  # psycopg2 dependencies
  && apk add --virtual build-deps gcc python3-dev musl-dev \
  && apk add sqlite \
  # Pillow dependencies
  && apk add jpeg-dev zlib-dev freetype-dev lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev \
  # CFFI dependencies
  && apk add libffi-dev openssl-dev py-cffi \
  # Translations dependencies
  && apk add gettext

# Requirements are installed here to ensure they will be cached.
COPY ./requirements /requirements
RUN pip install -r /requirements/local.txt

COPY ./compose/production/django/entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r//' /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY ./compose/production/django/celery/run_worker.sh /run_worker.sh
RUN sed -i 's/\r//' /run_worker.sh
RUN chmod +x /run_worker.sh

COPY ./compose/production/django/celery/run_beat.sh /run_beat.sh
RUN sed -i 's/\r//' /run_beat.sh
RUN chmod +x /run_beat.sh

COPY ./compose/local/django/start.sh /start.sh
RUN sed -i 's/\r//' /start.sh
RUN chmod +x /start.sh

WORKDIR /app

ENTRYPOINT ["/entrypoint.sh"]
