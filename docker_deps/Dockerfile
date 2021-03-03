FROM swaggerapi/swagger-codegen-cli:2.4.13 as intermediate
WORKDIR /app
ARG sempver=none
COPY docker_deps docker_deps
RUN mkdir output
RUN sed -i "s/VERSION/$sempver/" /app/docker_deps/*-python.json
RUN cat /app/docker_deps/*-python.json
RUN java -jar /opt/swagger-codegen-cli/swagger-codegen-cli.jar generate --config /app/docker_deps/config-python.json -o /app/output/python_config -i /app/docker_deps/semp_config/${sempver}/semp-v2-swagger-config.yaml -l python -t /app/docker_deps/templates
RUN test -f /app/docker_deps/semp_config/${sempver}/semp-v2-swagger-action.yaml && java -jar /opt/swagger-codegen-cli/swagger-codegen-cli.jar generate --config /app/docker_deps/action-python.json -o /app/output/python_action -i /app/docker_deps/semp_config/${sempver}/semp-v2-swagger-action.yaml -l python -t /app/docker_deps/templates || :
RUN test -f /app/docker_deps/semp_config/${sempver}/semp-v2-swagger-monitor.yaml && java -jar /opt/swagger-codegen-cli/swagger-codegen-cli.jar generate --config /app/docker_deps/monitor-python.json -o /app/output/python_monitor -i /app/docker_deps/semp_config/${sempver}/semp-v2-swagger-monitor.yaml -l python -t /app/docker_deps/templates || :

FROM python:3-slim as pyintermediate
COPY --from=intermediate /app/output /app/output/
WORKDIR /app/output
RUN mkdir tmp
#RUN sed -i "s/long_description=\"\"\"\(.*\)\"\"\"/"
# cat setup.py | sed  '/long_description="""/,/"""$/d'
RUN cd python_config; pip install -r requirements.txt; python setup.py bdist_wheel --universal; cp dist/*.whl ../tmp; cd ..
RUN ls
RUN ls /app/output/
RUN test -d python_action && cd /app/output/python_action; python setup.py bdist_wheel --universal; cp dist/*.whl ../tmp; cd .. || :
RUN test -d python_monitor && cd /app/output/python_monitor; python setup.py bdist_wheel --universal; cp dist/*.whl ../tmp; cd .. || :

FROM ubuntu:20.04
RUN apt-get update && apt-get -y install python3-dev
RUN apt-get -y install python3-pip
WORKDIR /app
ARG sempver=none
COPY --from=pyintermediate /app/output/python_config/setup.py /tmp/
COPY --from=pyintermediate /app/output/tmp/*.whl /tmp/
COPY .pypirc /root
RUN pwd
RUN echo $HOME
RUN ls /tmp
COPY requirements.txt requirements.txt
RUN python3 -m pip install --upgrade pip setuptools wheel twine
WORKDIR /tmp
RUN twine upload --repository testpypi /tmp/*.whl --verbose
#pip3 install --index-url https://test.pypi.org/simple/ solace_semp_config-${sempver}-py2.py3-none-any.whl
#RUN test -f /tmp/solace_semp_action-${sempver}-py2.py3-none-any.whl && pip3 install --index-url https://test.pypi.org/simple/ /tmp/solace_semp_action-${sempver}-py2.py3-none-any.whl || :
#RUN test -f /tmp/solace_semp_monitor-${sempver}-py2.py3-none-any.whl && pip3 install --index-url https://test.pypi.org/simple/ /tmp/solace_semp_monitor-${sempver}-py2.py3-none-any.whl || :

#RUN pip3 install -r requirements.txt
#COPY sp sp
#COPY pysolpro.py .
#RUN pip3 install /tmp/solace_semp_config-${sempver}-py2.py3-none-any.whl

ENTRYPOINT ["python3", "pysolpro.py"]