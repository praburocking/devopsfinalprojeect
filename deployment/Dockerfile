FROM teracy/ubuntu:16.04-dind-17.06.0-ce
RUN apt-get -y update
RUN apt-get install -y openssh-server
RUN apt-get install -y python3
RUN apt-get install -y sudo
RUN apt-get install -y nodejs
RUN apt-get install -y net-tools
RUN apt-get -y install git

RUN echo 'root:root' |chpasswd
RUN sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN useradd -m -s /bin/bash -G sudo -p $(openssl passwd -1 pass123) deploy
RUN service ssh start

EXPOSE 22
COPY project app/
ENTRYPOINT /usr/sbin/sshd -D && node server.js
