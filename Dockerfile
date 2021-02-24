FROM swaggerapi/swagger-codegen-cli:2.4.13 as intermediate
WORKDIR /app
ARG sempver=none
COPY docker_deps docker_deps
RUN mkdir output
RUN sed -i "s/VERSION/$sempver/" /app/docker_deps/*-python.json
RUN cat /app/docker_deps/*-python.json
RUN  java -jar /opt/swagger-codegen-cli/swagger-codegen-cli.jar generate --config /app/docker_deps/config-python.json -o /app/output/python_config -i /app/docker_deps/semp_config/${sempver}/semp-v2-swagger-config.yaml -l python
RUN test -f "/app/docker_deps/semp_config/${sempver}/semp-v2-swagger-action.yaml" && java -jar /opt/swagger-codegen-cli/swagger-codegen-cli.jar generate --config /app/docker_deps/action-python.json -o /app/output/python_action -i /app/docker_deps/semp_config/${sempver}/semp-v2-swagger-action.yaml -l python || :
RUN test -f "/app/docker_deps/semp_config/${sempver}/semp-v2-swagger-monitor.yaml" && java -jar /opt/swagger-codegen-cli/swagger-codegen-cli.jar generate --config /app/docker_deps/monitor-python.json -o /app/output/python_monitor -i /app/docker_deps/semp_config/${sempver}/semp-v2-swagger-monitor.yaml -l python || :

FROM python:3-slim as pyintermediate
COPY --from=intermediate /app/output /app/output
WORKDIR /app/output
RUN mkdir tmp
RUN cd python_config; pip install -r requirements.txt; python setup.py bdist_wheel --universal; cp dist/*.whl ../tmp; cd ..
RUN ls
RUN test -d "/app/output/python_action" && "cd python_action; python setup.py bdist_wheel --universal; cp dist/*.whl ../tmp; cd .." || :
RUN test -d "/app/output/python_monitor" && "cd python_monitor; python setup.py bdist_wheel --universal; cp dist/*.whl ../tmp; cd .." || :

FROM python:alpine3.13
WORKDIR /app
ARG sempver=none
COPY --from=pyintermediate /app/output/tmp/*.whl /tmp
RUN pwd
RUN ls /tmp
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY sp sp
COPY pysolpro.py .
RUN pip3 install /tmp/solace_semp_config-${sempver}-py2.py3-none-any.whl
RUN test -f "/tmp/solace_semp_action-${sempver}-py2.py3-none-any.whl" && pip3 install /tmp/solace_semp_action-${sempver}-py2.py3-none-any.whl || :
RUN test -f "/tmp/solace_semp_monitor-${sempver}-py2.py3-none-any.whl" && pip3 install /tmp/solace_semp_monitor-${sempver}-py2.py3-none-any.whl || :

ENTRYPOINT ["python3", "pysolpro.py"]