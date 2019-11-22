FROM tiangolo/uvicorn-gunicorn:python3.7-alpine3.8
WORKDIR /app/wfs
COPY . /app/wfs/
EXPOSE 8080
RUN pip install -r requirements.txt
CMD ["uvicorn", "main:app"]