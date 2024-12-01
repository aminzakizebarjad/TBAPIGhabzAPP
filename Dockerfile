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

# pandas uses  python-dateutil=>2.9.0 , also tb-rest-client uses python-dateutil==2.5.3, we will use two req files to prevent conflicts
# first tb-rest client must get installed with lower version dependency, then other modules in requirements.txt
# we will encounter dependeny error but no problem

# pip problem resolved in IRAN, so we will use usual requirements file instead of from source
# from source is commented accordingly
COPY ./requirement1.txt /code/requirement1.txt
COPY ./requirements.txt /code/requirements.txt
#COPY ./requirements_from_source.txt /code/requirements.txt

RUN pip3 install -r /code/requirement1.txt
RUN pip3 install -r /code/requirements.txt
COPY ./app /code/app

# run flask with gunicorn
CMD ["gunicorn", "--conf", "app/gunicorn_conf.py", "--bind", "0.0.0.0:80", "app.app:app"]
# run flask solely
#CMD ["flask", "--app", "app.main:app", "run", "-p", "3000"]