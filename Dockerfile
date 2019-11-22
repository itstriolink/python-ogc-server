FROM tiangolo/uvicorn-gunicorn:python3.7-alpine3.8
COPY . ./
WORKDIR /src/miniwfs
RUN pip install -r requirements.txt
EXPOSE 8080
VOLUME ["/var/miniwfs"]
ENTRYPOINT ["./miniwfs", "--port=8080"]
CMD ["--collections=castles=/var/miniwfs/castles.geojson"]