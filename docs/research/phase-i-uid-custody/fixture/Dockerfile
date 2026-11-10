FROM python@sha256:5e2bdb1b0d542d5039cffb8181c65930093949194a65c365dfb1b0fe13a4fa5b
WORKDIR /opt/probe
COPY src/ /opt/probe/src/
COPY driver.py worker_agent.py owner_supervisor.py /opt/probe/
RUN chmod -R u+rwX,go+rX /opt/probe && find /opt/probe -type f -exec chmod 0644 {} + && find /opt/probe -type d -exec chmod 0755 {} +
ENTRYPOINT ["python", "-I", "-B", "/opt/probe/driver.py"]
