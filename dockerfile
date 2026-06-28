ARG BUILD_FROM
FROM $BUILD_FROM
RUN apk add --no-cache python3 py3-pip
COPY src/ /app/
COPY requirements.txt /app/
RUN pip3 install -r /app/requirements.txt
CMD ["python3", "/app/main.py"]
