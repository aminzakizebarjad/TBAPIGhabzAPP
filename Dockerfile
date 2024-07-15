#FROM ubuntu:latest
#LABEL authors="AMIN"
#
#ENTRYPOINT ["top", "-b"]
# TODO: create the requirement.txt by freezing python
FROM docker.arvancloud.ir/python:3.10-slim
#FROM python:3.10-alpine

RUN apt update
RUN apt install git -y

WORKDIR /code

#COPY ./requirements.txt /code/requirements.txt
COPY ./requirements_from_source.txt /code/requirements.txt

RUN pip3 install -r /code/rdocker equirements.txt
COPY ./app /code/app

# run flask with gunicorn
CMD ["gunicorn", "--conf", "app/gunicorn_conf.py", "--bind", "0.0.0.0:80", "app.main:app"]
# run flask solely
#CMD ["flask", "--app", "app.main:app", "run", "-p", "3000"]