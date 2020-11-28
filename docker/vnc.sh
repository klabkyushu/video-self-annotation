#!/bin/bash

export USER="user"
password="password"

mkdir -p $HOME/.vnc

/usr/bin/expect <<EOF
spawn "/opt/TurboVNC/bin/vncpasswd"
expect "Password:"
send "$password\r"
expect "Verify:"
send "$password\r"
expect "Would you like to enter a view-only password (y/n)? "
send "n\r"
expect eof
exit
EOF

# Set up vncserver
echo "#!/bin/bash
xrdb $HOME/.Xresources
startxfce4 &
" >> $HOME/.vnc/xstartup

chmod +x $HOME/.vnc/xstartup

/opt/TurboVNC/bin/vncserver -geometry 1600x900
