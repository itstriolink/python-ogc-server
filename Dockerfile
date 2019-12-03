FROM tiangolo/uvicorn-gunicorn:python3.7-alpine3.8
WORKDIR /app/wfs
COPY requirements.txt /app/wfs/
RUN apk add build-base python-dev py-pip jpeg-dev zlib-dev
ENV LIBRARY_PATH=/lib:/usr/lib
RUN pip install -r requirements.txt
COPY . /app/wfs
EXPOSE 8000
CMD ["uvicorn", "ogc_api.main:app", "--host", "0.0.0.0", "--port", "8000"]