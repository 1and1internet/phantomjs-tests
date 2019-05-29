FROM 1and1internet/debian-9:latest

ARG PHANTOMJS=phantomjs-2.1.1-linux-x86_64

# Other potential requirements for phantomjs are...
#   libsqlite3 libicu libfreetype6 libssl libpng libjpeg libx11 libxext
# I've only installed libfontconfig1 as that's the minimum requirement and meets our needs

RUN apt-get update \
    && apt-get install -y curl tar bzip2 python3 python3-dev python3-setuptools libfontconfig1 sudo git \
    && curl https://bootstrap.pypa.io/get-pip.py | python3 \
    && cd / \
    && curl -L https://bitbucket.org/ariya/phantomjs/downloads/${PHANTOMJS}.tar.bz2 | tar jxvf - \
    && cd /${PHANTOMJS} \
    && chmod -R 777 /usr/local \
    && chmod -R 755 /hooks \
    && cd /root \
    && apt-get update -q \
    && apt-get install -y \
            apt-transport-https \
            ca-certificates \
            curl \
            gnupg2 \
            libpq-dev \
            chromedriver \
    && curl -fsSL https://download.docker.com/linux/debian/gpg --output docker-gpg-key \
    && apt-key add docker-gpg-key \
    && apt-key fingerprint 0EBFCD88 | grep "9DC8 5822 9FC7 DD38 854A  E2D8 8D81 803C 0EBF CD88" \
    && echo "deb [arch=amd64] https://download.docker.com/linux/debian stretch stable" >> /etc/apt/sources.list \
    && apt-get update -q \
    && apt-get install docker-ce \
    && apt-get clean -q -y \
    && rm -rf /var/lib/apt/lists/* \
    && rm /hooks/entrypoint-pre.d/00_check_euid

COPY files /
RUN chmod +x /usr/local/bin/* \
    && cd /root \
    && sha1sum -c sha1sums.txt \
    && pip3 install -q --upgrade pip kubernetes selenium \
    && cd /root/testpack_helper_library_module \
    && pip3 install -q .

ARG PROXY
ENV PATH=${PATH}:/${PHANTOMJS}/bin \
    CI_WORKSPACE=/mnt \
    GIT_REPO="https://github.com" \
    PROXY=${PROXY} \
    K8S_TEST_NAMESPACE=paas-library-develop

WORKDIR /mnt
