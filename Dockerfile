FROM python:3.10-slim as python

FROM python
RUN pip install pipenv
WORKDIR /src
COPY . ./
RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy
ENTRYPOINT ["pipenv","run","python","-u","-m","fhir_transformer","--watch"]
#ENTRYPOINT [ "pipenv","run","python", "-u","app.py" ]