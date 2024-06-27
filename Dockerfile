#FROM ubuntu:latest
#LABEL authors="AMIN"
#
#ENTRYPOINT ["top", "-b"]
# TODO: create the requirement.txt by freezing python
FROM docker.arvancloud.ir/python:3.11

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

CMD ["gunicorn", "--conf", "app/gunicorn_conf.py", "--bind", "0.0.0.0:80", "app.main:app"]