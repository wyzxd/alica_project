FROM python:3.12.3

WORKDIR /app
COPY . /app

EXPOSE 5000

RUN pip install -r requirements.txt
CMD FLASK_APP=main.py flask run --host="::"
