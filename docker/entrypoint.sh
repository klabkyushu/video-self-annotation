#!/bin/bash

password="password"
uid="2004"
gid="2000"
ssh_pub_key="ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDHtCiHFN/OiOKJNRQZOXekZB2P97MAtCe0NqwFKiaNWXAF9q8Yek8NzPMXNgBJQ30a6kqunuPZxjzH6YybpPB+PJ0jcqIRBiTzJUIubU7MZIbKrtHmFfmEMGHO218g/LIvVXRmn/TVn6T8VVAJOXsrgLchuYou+24yXmQmQPMTc69zKndOr2GPRIF+JteG8+KiuUBwCYub4nWqdPBy6r+5I2p7PhHPgStqnutzsF/hhu0sz01kqH3nCLAEUINFJ3FjOpcsF5x4/s+kIDF4qKb/QVrq1sPkKB5l13gs663LBDmWUB93B12nXsr9+VXhzwBle5EmC3hQ1mc0rrnz5/Zd drpap@DESKTOP-R93UP31"

# Set up PATH
echo "export PATH=/home/user/.local/bin:$PATH" >> /home/user/.bashrc
echo "export LC_ALL=C.UTF-8" >> /home/user/.bashrc
echo "export LANG=C.UTF-8" >> /home/user/.bashrc

# Set up uid, gid.
mkdir -p /tmp/user
usermod -d /tmp/user user
usermod -u $uid user
groupmod -g $gid user
usermod -d /home/user user
usermod -aG sudo user
echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers
echo "user:$password" | chpasswd

# Set up the SSH key.
mkdir -p /home/user/.ssh
echo $ssh_pub_key > /home/user/.ssh/authorized_keys
echo "ChallengeResponseAuthentication no" >> /etc/ssh/sshd_config
echo "PasswordAuthentication no" >> /etc/ssh/sshd_config
echo "UsePAM no" >> /etc/ssh/sshd_config
echo "PermitRootLogin no" >> /etc/ssh/sshd_config
service ssh start

# Set up xfce terminal
/usr/bin/expect <<EOF
spawn /usr/bin/update-alternatives --config x-terminal-emulator
send "4\r"
expect eof
exit
EOF

./install.sh
pip install -e ./annotation

# Modify permissions.
chown $uid:$gid /home/user
chown $uid:$gid /home/user/.*
chown $uid:$gid $project_root/vendors/video-maskrcnn/maskrcnn_benchmark/external/tracking/SOT/SiamDW/snapshot/CIResNet22_RPN.pth
chown -R $uid:$gid $project_root/annotation
chown -R $uid:$gid $project_root/interface

# Start vnc server
sudo -H -u user bash docker/vnc.sh

echo "All done."

while true; do sleep 30; done;
