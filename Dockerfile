FROM ubuntu:22.04
RUN apt-get update && \
    apt-get -y install python3-pip python3-lxml libomp-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt
COPY src/ src/
ENTRYPOINT ["python3", "/app/src/main.py"]