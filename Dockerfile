FROM python:3.11
# set a directory for the app
ENV PYTHONUNBUFFERED True
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

# copy all the files to the container
WORKDIR . 

COPY requirements.txt .

# install dependencies
RUN pip install -r requirements.txt

# cd into a dir

ENV PORT 8080

COPY . .
RUN chmod a+x run.sh
#CMD ["./run.sh"]
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main_app:app
#CMD ["python","upload_logs.py"]