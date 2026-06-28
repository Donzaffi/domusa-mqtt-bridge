ARG BUILD_FROM
FROM ${BUILD_FROM}

WORKDIR /app

RUN apk add --no-cache python3 py3-pip

RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH"

COPY src/ /app/
COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "/app/main.py"]
