FROM golang as supervisorgo
MAINTAINER brian.wilkinson@1and1.co.uk
WORKDIR /go/src/github.com/1and1internet/supervisorgo
RUN git clone https://github.com/1and1internet/supervisorgo.git . \
	&& go build -o release/supervisorgo \
	&& echo "supervisorgo successfully built"

FROM ubuntu:latest
COPY --from=supervisorgo /go/src/github.com/1and1internet/supervisorgo/release/supervisorgo /usr/bin/supervisorgo
ARG PHANTOMJS=phantomjs-2.1.1-linux-x86_64

RUN \
    apt-get update \
    && apt-get install -y wget tar bzip2 npm default-jre nodejs netcat \
    build-essential g++ flex bison gperf ruby perl \
    libsqlite3-dev libfontconfig1-dev libicu-dev libfreetype6 libssl-dev \
    libpng-dev libjpeg-dev python3 python3-pip libx11-dev libxext-dev \
    && cd / \
    && wget https://bitbucket.org/ariya/phantomjs/downloads/${PHANTOMJS}.tar.bz2 \
    && tar xvf /${PHANTOMJS}.tar.bz2 \
    && cd /${PHANTOMJS} \
    && ln -s /usr/bin/nodejs /usr/bin/node \
    && npm install selenium-standalone@latest -g \
    && selenium-standalone install \
    && update-alternatives --install /usr/bin/supervisord supervisord /usr/bin/supervisorgo 1

ENV PATH=${PATH}:/${PHANTOMJS}/bin \
    TESTS_DIR=/tmp/tests

WORKDIR /mnt
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisor.conf"]

COPY files /