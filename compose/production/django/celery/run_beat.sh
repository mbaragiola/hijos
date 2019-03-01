#!/bin/sh

sleep 10

celery beat -A hijos -l INFO -S django_celery_beat.schedulers:DatabaseScheduler
