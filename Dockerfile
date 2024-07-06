FROM python:3.12.2

WORKDIR /app

RUN pip install fastapi pymongo python-dotenv uvicorn email-validator python-multipart 


COPY . .


EXPOSE 8080


CMD [ "uvicorn", "main:app","--host", "0.0.0.0","--port","8080", "--reload" ]