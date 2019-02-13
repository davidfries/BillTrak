FROM ubuntu:18.10



RUN apt-get update
RUN apt-get install -y python3 python3-dev python3-pip nginx
# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /app/requirements.txt

WORKDIR /app
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
RUN pip3 install gunicorn
COPY . /app

ENTRYPOINT [ "python3" ]

