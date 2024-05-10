FROM python:alpine
RUN pip install pipenv pyenv
COPY Pipfile* /tmp/
WORKDIR /tmp/
RUN pipenv sync
COPY . /tmp/
CMD python /tmp/src/Core.py
