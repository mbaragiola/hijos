#!/bin/sh

sleep 10

celery worker -A hijos -Q default -n default@%h -l INFO -E
