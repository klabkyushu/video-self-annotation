#!/bin/bash

password="password"
uid="1001"
gid="1000"
ssh_pub_key="ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDHtCiHFN/OiOKJNRQZOXekZB2P97MAtCe0NqwFKiaNWXAF9q8Yek8NzPMXNgBJQ30a6kqunuPZxjzH6YybpPB+PJ0jcqIRBiTzJUIubU7MZIbKrtHmFfmEMGHO218g/LIvVXRmn/TVn6T8VVAJOXsrgLchuYou+24yXmQmQPMTc69zKndOr2GPRIF+JteG8+KiuUBwCYub4nWqdPBy6r+5I2p7PhHPgStqnutzsF/hhu0sz01kqH3nCLAEUINFJ3FjOpcsF5x4/s+kIDF4qKb/QVrq1sPkKB5l13gs663LBDmWUB93B12nXsr9+VXhzwBle5EmC3hQ1mc0rrnz5/Zd drpap@DESKTOP-R93UP31"

# Set up PATH
echo "export PATH=$PATH" >> /home/user/.bashrc

# Set up uid, gid.
usermod -u $uid user
groupmod -g $gid user
echo "user:$password" | chpasswd

# Set up the SSH key.
mkdir -p /home/user/.ssh
echo $ssh_pub_key > /home/user/.ssh/authorized_keys
service ssh start

# Set up xfce terminal
/usr/bin/expect <<EOF
spawn /usr/bin/update-alternatives --config x-terminal-emulator
send "4\r"
expect eof
exit
EOF

# Download pre-trained models
# https://drive.google.com/file/d/10bqv7fUeUEdT1Q9T617QTcttit5EJi76/view
project_root=$(pwd)
mkdir -p $project_root/annotation/CityScapes/val/Dataset/Images
mkdir -p $project_root/annotation/CityScapes/val/Raw
cd $project_root/annotation/CityScapes/val/
fileid="10bqv7fUeUEdT1Q9T617QTcttit5EJi76"
filename="Initial_model.zip"
curl -c ./cookie -s -L "https://drive.google.com/uc?export=download&id=${fileid}" > /dev/null
curl -Lb ./cookie "https://drive.google.com/uc?export=download&confirm=`awk '/download/ {print $NF}' ./cookie`&id=${fileid}" -o ${filename}
rm ./cookie
unzip Initial_model.zip
rm Initial_model.zip

# CIResNet22_RPN.pth: https://drive.google.com/file/d/1tBllNtv-90Ih2EP_lnRCBzxnZeFPRnPx/view?usp=sharing
mkdir -p $project_root/vendors/video-maskrcnn/maskrcnn_benchmark/external/tracking/SOT/SiamDW/snapshot
cd $project_root/vendors/video-maskrcnn/maskrcnn_benchmark/external/tracking/SOT/SiamDW/snapshot
fileid="1tBllNtv-90Ih2EP_lnRCBzxnZeFPRnPx"
filename="CIResNet22_RPN.pth"
curl -c ./cookie -s -L "https://drive.google.com/uc?export=download&id=${fileid}" > /dev/null
curl -Lb ./cookie "https://drive.google.com/uc?export=download&confirm=`awk '/download/ {print $NF}' ./cookie`&id=${fileid}" -o ${filename}
rm ./cookie

# Modify permissions.
chown -R $uid:$gid /home/user

echo "All done."

while true; do sleep 30; done;
