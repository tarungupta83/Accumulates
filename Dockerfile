FROM python:3.9.7-slim-buster

COPY requirements.txt /main/

WORKDIR /main

RUN pip install --upgrade pip \
    &&  pip install -r requirements.txt

COPY utils ./utils/
COPY assets ./assets/
COPY .streamlit ./.streamlit/
COPY streamlit_main.py .

EXPOSE 8080

CMD ["streamlit", "streamlit_main.py"]

# docker build -t=don_vgg:0.1 .
# docker run --shm-size=8gb --rm --gpus all don_vgg:0.1
# you can increase /dev/shm size by passing '--shm-size=10.24gb' to 'docker run'
