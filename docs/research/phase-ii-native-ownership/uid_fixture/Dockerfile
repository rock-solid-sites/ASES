FROM ases-uid-custody:phase-i-20261110
USER 0:0
WORKDIR /opt/owned-src
COPY src/ /opt/owned-src/
RUN find /opt/owned-src -type d -exec chmod 0755 {} + && find /opt/owned-src -type f -name '*.py' -exec chmod 0644 {} +
ENTRYPOINT ["/usr/local/bin/python", "-I", "-B", "/opt/owned-src/docs/research/phase-ii-native-ownership/uid_fixture/driver.py"]
