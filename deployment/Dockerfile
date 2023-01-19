FROM teracy/ubuntu:16.04-dind-17.06.0-ce
#FROM alpine:latest
# RUN apk update
# RUN apk add --update --no-cache openssh 
# RUN echo 'PasswordAuthentication yes' >> /etc/ssh/sshd_config
# # RUN sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config
# # RUN useradd -m -s /bin/bash -G sudo -p $(openssl passwd -1 eee) ssluser
# #RUN apk add sudo
# RUN apk add python3
# RUN apk add doas
# RUN adduser -h /home/deploy -s /bin/sh -D deploy
# RUN echo 'deploy:deploy123' | chpasswd
# RUN echo 'permit deploy as root' > /etc/doas.d/doas.conf
# EXPOSE 22
# USER deploy
# #ENTRYPOINT service ssh start && while true; do sleep 1; done
# COPY entrypoint.sh /
# ENTRYPOINT ["/entrypoint.sh"]

# RUN apk add --update --no-cache openssh 
# RUN echo 'PasswordAuthentication yes' >> /etc/ssh/sshd_config
# RUN adduser -h /home/deploy -s /bin/sh -D deploy
# RUN echo -n 'deploy:pass123' | chpasswd
# RUN sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config
# RUN apk --no-cache add git
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

#RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd

# ENTRYPOINT ["/entrypoint.sh"]
EXPOSE 22
# COPY entrypoint.sh /
# RUN mkdir app
COPY project app/
ENTRYPOINT /usr/sbin/sshd -D && node server.js
