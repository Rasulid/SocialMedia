FROM python:3.10

WORKDIR /app

COPY . .

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

ENV PYTHONPATH "${PYTHONPATH}:/app/"
ENV PYTHONPATH "${PYTHONPATH}:/app/api"

RUN mkdir -p /app/api/media

COPY media /app/api/media

RUN chmod a+x api/app.sh


WORKDIR /app/api

CMD alembic upgrade head && uvicorn main:app --host "0.0.0.0" --port 8000 --workers 4 --reload
