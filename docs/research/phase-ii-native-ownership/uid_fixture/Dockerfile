FROM ases-uid-custody:phase-i-20261110
USER 0:0
WORKDIR /opt/owned-src
COPY . /opt/owned-src/
RUN chmod 0755 /opt/owned-src /opt/owned-src/docs /opt/owned-src/docs/research /opt/owned-src/docs/research/phase-ii-native-ownership /opt/owned-src/docs/research/phase-ii-native-ownership/uid_fixture && chmod 0644 /opt/owned-src/docs/research/phase-ii-native-ownership/uid_fixture/*.py /opt/owned-src/docs/research/phase-ii-native-ownership/*.py
ENTRYPOINT ["/usr/local/bin/python", "-I", "-B", "/opt/owned-src/docs/research/phase-ii-native-ownership/uid_fixture/driver.py"]
