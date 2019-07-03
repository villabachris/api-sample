FROM python:3.6
ENV PYTHONBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
ADD assets /code/
RUN pip install -r requirements.txt
ADD . /code/
WORKDIR /code/

EXPOSE 8057

CMD ["python", "app.py"]