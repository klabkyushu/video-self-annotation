FROM pytorch/pytorch:1.2-cuda10.0-cudnn7-devel

# Set up user
RUN groupadd user && \
    useradd -m -g user -s /bin/bash user

# Set up SSH and VNC
ENV DEBIAN_FRONTEND=noninteractive
ENV DEBCONF_NONINTERACTIVE_SEEN=true
RUN apt-get update && \
    # Common packages
    apt-get install -y curl expect cmake \
    # ssh
    openssh-server \
    # xfce desktop enviroment
    xfce4 xfce4-goodies && \
    curl -O https://jaist.dl.sourceforge.net/project/turbovnc/2.2.5/turbovnc_2.2.5_amd64.deb && \
    dpkg -i turbovnc_2.2.5_amd64.deb && \
    rm turbovnc_2.2.5_amd64.deb

WORKDIR /home/user/video-self-annotation

# Install dependencies
COPY requirements.txt install.sh ./
COPY vendors ./vendors
RUN apt-get install -y \
    # OpenCV dependencies
    libgtk2.0-dev pkg-config libavcodec-dev libavformat-dev libswscale-dev && \
    # video-self-annotation dependencies
    pip install -r requirements.txt && \
    cd vendors/cocoapi/PythonAPI && \
    python setup.py build_ext install && \
    cd ../../apex && \
    pip install -v --no-cache-dir --global-option="--cpp_ext" --global-option="--cuda_ext" . && \ 
    cd ../video-maskrcnn && \
    python setup.py build develop

CMD [ "/bin/bash", "docker/entrypoint.sh" ]
