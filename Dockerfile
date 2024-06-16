FROM python:3.11-alpine
RUN pip install pipenv
COPY Pipfile* /tmp/
WORKDIR /tmp/
RUN pipenv sync
COPY . /tmp/
CMD python /tmp/src/Core.py
