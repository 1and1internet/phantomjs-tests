FROM 1and1internet/debian-8:latest

ARG PHANTOMJS=phantomjs-2.1.1-linux-x86_64

# Other potential requirements for phantomjs are...
#   libsqlite3 libicu libfreetype6 libssl libpng libjpeg libx11 libxext
# I've only installed libfontconfig1 as that's the minimum requirement and meets our needs

COPY files /
RUN apt-get update \
    && apt-get install -y curl tar bzip2 python3 python3-pip libfontconfig1 \
    && cd / \
    && curl -L https://bitbucket.org/ariya/phantomjs/downloads/${PHANTOMJS}.tar.bz2 | tar jxvf - \
    && cd /${PHANTOMJS} \
    && update-alternatives --install /usr/bin/supervisord supervisord /usr/bin/supervisorgo 1 \
	&& apt-get clean \
	&& rm -rf /var/lib/apt/lists/* \
	&& chmod -R 777 /usr/local \
	&& chmod +x /usr/local/bin/test_runner

ENV PATH=${PATH}:/${PHANTOMJS}/bin \
    TESTS_DIR=/tmp/tests

WORKDIR /mnt
#ENTRYPOINT ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf"]
