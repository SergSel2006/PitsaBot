FROM python:3.11-alpine
RUN pip install pipenv
COPY Pipfile* /tmp/
WORKDIR /tmp/
RUN pipenv lock
RUN cd /tmp && pipenv requirements > requirements.txt
RUN pip install -r /tmp/requirements.txt
COPY . /tmp/
CMD python /tmp/src/Core.py
