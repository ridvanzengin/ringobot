FROM python:3.11.9

WORKDIR /

COPY requirements.txt /
RUN pip install -r requirements.txt

COPY . /pythonProject
WORKDIR /pythonProject

CMD [ "python", "-u", "webApp.py" ]