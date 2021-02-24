FROM python:3-slim
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY sp sp
COPY pysolpro.py .
COPY docker_deps docker_deps
RUN pip3 install docker_deps/solace_semp_action-9.8.0.12-py2.py3-none-any.whl
RUN pip3 install docker_deps/solace_semp_config-9.8.0.12-py2.py3-none-any.whl
RUN pip3 install docker_deps/solace_semp_monitor-9.8.0.12-py2.py3-none-any.whl
#CMD ["python3", "./pysolpro.py"]
ENTRYPOINT ["python3", "pysolpro.py"]