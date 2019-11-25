FROM tiangolo/uvicorn-gunicorn:python3.7-alpine3.8
WORKDIR /app/wfs
COPY requirements.txt /app/wfs/
RUN pip install -r requirements.txt
COPY . /app/wfs
EXPOSE 8080
CMD ["uvicorn", "wfs_server.main:app"]