FROM adoptopenjdk:openj9 as intermediate
WORKDIR /app
ARG sempver=none
RUN curl https://repo1.maven.org/maven2/io/swagger/swagger-codegen-cli/2.4.13/swagger-codegen-cli-2.4.13.jar -o swagger-codegen-cli-2.4.13.jar
COPY docker_deps docker_deps
RUN mkdir output
RUN sed -i "s/VERSION/$sempver/" /app/docker_deps/config-*.json
RUN java -jar swagger-codegen-cli-2.4.13.jar generate --config /app/docker_deps/config-python.json -o /app/output/python_config -i /app/docker_deps/semp_config/$sempver/semp-v2-swagger-config.yaml -l python


FROM python:3-slim as pyintermediate
COPY --from=intermediate /app/output/python_config /app/python_config
WORKDIR /app/python_config
RUN pip install -r requirements.txt
RUN python setup.py bdist_wheel --universal

FROM python:alpine3.13
WORKDIR /app
ARG sempver=none
COPY --from=pyintermediate /app/python_config/dist/*.whl /tmp
RUN pwd
RUN ls /tmp
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY sp sp
COPY pysolpro.py .
RUN pip3 install /tmp/solace_semp_config-$sempver-py2.py3-none-any.whl


ENTRYPOINT ["python3", "pysolpro.py"]