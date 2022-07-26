FROM cytomine/software-python3-base

WORKDIR /app

COPY src/ .

ENTRYPOINT ["python", "/app/run.py"]