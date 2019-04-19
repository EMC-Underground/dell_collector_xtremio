FROM python:3.7.3-alpine3.9

COPY ./requirements.txt /

RUN pip install --no-cache-dir -r /requirements.txt

COPY ./xio_collector.py /

ENTRYPOINT ["python /xio_collector.py"]
