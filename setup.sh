#!/bin/bash

sudo raspi-config nonint do_camera 0
sudo apt update
sudo apt install python3-gpiozero python3-picamera python3-pip python3-pil git -y
sudo pip3 install twython --upgrade
sudo pip3 install pydrive
sudo pip3 install qrcode
cd ~
[ -d Pictures ] || mkdir Pictures
git clone https://github.com/raspberrypifoundation/jam-photobooth
crontab -l | { cat; echo "@reboot python3 /home/pi/jam-photobooth/photobooth.py &"; } | crontab -
sudo reboot
