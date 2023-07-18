FROM paperspace/fastapi-deployment:latest

WORKDIR /app

COPY main.py download.py start.py config.py requirements.txt ./

RUN pip3 install -U pip
RUN pip3 install -r requirements.txt

# try and download the model weights...
RUN python3 download.py

# May need to get the LD_LIBRARY_PATH to point to cudnn_ops_infer again

CMD ["python3", "start.py"]

