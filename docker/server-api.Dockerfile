FROM python:3.9-slim


# COPY ./server/requirements.txt requirements.txt
COPY ./server /server
# WORKDIR /server

RUN pip install --no-cache-dir --upgrade -r /server/requirements.txt

CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "8000"]
