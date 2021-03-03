FROM python:alpine3.13
WORKDIR /app
ARG sempver=none
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY sp sp
COPY pysolpro.py .
RUN pip3 install solace-semp-config==${sempver}
RUN pip3 install solace-semp-action==${sempver} || :
RUN pip3 install solace-semp-monitor==${sempver} || :

ENTRYPOINT ["python3", "pysolpro.py"]