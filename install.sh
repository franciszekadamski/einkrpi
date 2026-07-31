#!/usr/bin/bash


echo "Installing xserver-xorg-video-dummy"

sudo apt update
sudo apt install xserver-xorg-video-dummy

echo "Installing python requirements"

sudo pip3 install -r requirements.txt --break-system-packages

echo "Copying the dummy screen file"
if [ -z /etc/X11/xorg.conf.d/20-dummy.conf ]; then
    sudo cp dummy.conf /etc/X11/xorg.conf.d/20-dummy.conf
fi

echo "Installing einkrpi"

if [ ! -d $HOME/.local/share ]; then
    echo "Creating $HOME/.local/share directory"
    mkdir -p $HOME/.local/share
fi

if [ ! -d $HOME/.config/einkrpi ]; then
    echo "Creating $HOME/.config/einkrpi directory"
    mkdir -p $HOME/.config/einkrpi
fi

if [ -z $HOME/.config/einkrpi/config.env ];then
    echo "Creating config.env file at $HOME/.config/einkrpi/"
    echo "HOME=${HOME}" > $HOME/.config/einkrpi/config.env
fi

if [ ! -d $HOME/.local/share/einkrpi ]; then
    echo "Cloning einkrpi repository to $HOME/.local/share/"
    cd $HOME/.local/share
    git clone https://github.com/franciszekadamski/einkrpi.git
fi

cd $HOME/.local/share/einkrpi

git pull

echo "Attempting to stop, disable and remove einkrpi.service for systemd"
sudo systemctl stop einkrpi.service
sudo systemctl disable einkrpi.service
sudo rm /etc/systemd/einkrpi.service

echo "Installing einkrpi.service"
envsubst < $PWD/einkrpi.service.template | sudo tee /etc/systemd/system/einkrpi.service > /dev/null

sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable einkrpi.service
sudo systemctl start einkrpi.service
sudo systemctl status einkrpi.service

echo "Finished installation of einkrpi"
echo "The repository is located in $HOME/.local/share/einkrip directory"
echo "Additionally, /etc/systemd/system/einkrpi.service file has been created"
echo "Fake screen file created is /etc/X11/xorg.conf.d/20-dummy.conf"
