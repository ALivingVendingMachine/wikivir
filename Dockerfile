FROM python:3.6-slim
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD . /code/
RUN apt update
RUN apt install -y build-essential
RUN pip install -r requirements.txt
