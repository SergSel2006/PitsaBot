FROM python:alpine
RUN pip install pipenv
COPY Pipfile* /tmp/
RUN cd /tmp && pipenv requirements > requirements.txt
RUN pip install -r /tmp/requirements.txt
COPY . /tmp/PitsaBot
WORKDIR /tmp/PitsaBot
CMD python /tmp/PitsaBot/src/Core.py

