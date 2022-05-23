FROM cytomine/software-python3-base

ADD exportation.py /app/exportation.py

ENTRYPOINT ["python", "/app/exportation.py"]