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
    && chmod -R 777 /usr/local \
    && chmod +x /usr/local/bin/* \
    && chmod -R 755 /hooks \
    && cd /root \
    && apt-get update -q \
    && apt-get install -y \
            apt-transport-https \
            ca-certificates \
            curl \
            gnupg2 \
            software-properties-common \
    && curl -fsSL https://download.docker.com/linux/$(. /etc/os-release; echo "$ID")/gpg --output docker-gpg-key \
    && sha1sum -c sha1sums.txt \
    && verify_gpg_key_fingerprint /root/docker-gpg-key '9DC8 5822 9FC7 DD38 854A  E2D8 8D81 803C 0EBF CD88' \
    && apt-key add /root/docker-gpg-key \
    && add-apt-repository \
            "deb [arch=amd64] https://download.docker.com/linux/$(. /etc/os-release; echo "$ID") \
            $(lsb_release -cs) \
            stable"  \
    && apt-get update -q \
    && apt-get install docker-ce \
    && apt-get clean -q -y \
    && rm -rf /var/lib/apt/lists/* \     
    && rm /hooks/entrypoint-pre.d/00_check_euid

ENV PATH=${PATH}:/${PHANTOMJS}/bin \
    CI_WORKSPACE=/mnt

WORKDIR /mnt
