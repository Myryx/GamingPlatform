# -*- mode: ruby -*-
# vi: set ft=ruby :

# Server development environment installation

# require 'yaml'
# settings = YAML.load_file 'vagrant_config.yml'


$create_downloads_folder = <<SCRIPT
  echo "Creating Downloads folder..."
  mkdir -p /vagrant/Downloads
SCRIPT

$update_os = <<SCRIPT
  echo "Updating the image..."
  sudo apt-get update
  sudo DEBIAN_FRONTEND=noninteractive apt-get -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" upgrade
  sudo apt-get dist-upgrade -y
SCRIPT


$create_swap = <<SCRIPT
  echo "Creating swap..."
  sudo dd if=/dev/zero of=/var/swap.img bs=1024k count=1000
  sudo mkswap /var/swap.img
  sudo chmod 0600 /var/swap.img
  sudo swapon /var/swap.img
SCRIPT


$set_encoding = <<SCRIPT
  echo "Setting up encoding..."
  sudo echo "LANG=en_US.UTF-8" >> /etc/environment
  sudo echo "LANGUAGE=en_US.UTF-8" >> /etc/environment
  sudo echo "LC_ALL=en_US.UTF-8" >> /etc/environment
  sudo echo "LC_CTYPE=en_US.UTF-8" >> /etc/environment
SCRIPT


$install_gui_xfce4 = <<SCRIPT
  echo "Installing xfce4..."
  sudo apt-get install -y xfce4 virtualbox-guest-dkms virtualbox-guest-utils virtualbox-guest-x11
  sudo apt-get install -y gnome-icon-theme-full tango-icon-theme
  sudo sed -ie "s:allowed_users=.*$:allowed_users=anybody:" /etc/X11/Xwrapper.config
SCRIPT


$autostart_gui_xfce4 = <<SCRIPT
  echo "Setting xfce4 autostart..."
  sudo echo "start on runlevel [23]" >> /etc/init/Xinit.conf
  sudo echo "stop on runlevel [!23]" >> /etc/init/Xinit.conf
  sudo echo "respawn" >> /etc/init/Xinit.conf
  sudo echo "exec /bin/openvt -fwc 6 -- /bin/su -c /usr/bin/startx vagrant" >> /etc/init/Xinit.conf
SCRIPT


$install_gui_unity = <<SCRIPT
  echo "Installing Unity..."
  sudo apt-get install -y --no-install-recommends ubuntu-desktop virtualbox-guest-dkms virtualbox-guest-utils virtualbox-guest-x11
SCRIPT

$fix_dictionaries = <<SCRIPT
  echo "Fixing dictionaries..."
  sudo /usr/share/debconf/fix_db.pl
  sudo dpkg-reconfigure dictionaries-common
  sudo apt-get upgrade -y
SCRIPT

$install_vb_guest_additions = <<SCRIPT
  echo "Installing VirtualBox Guest Additions..."
  sudo apt-get install -y linux-headers-$(uname -r) build-essential dkms
  wget -c -nc -O /vagrant/Downloads/VBoxGuestAdditions_5.1.14.iso http://download.virtualbox.org/virtualbox/5.1.14/VBoxGuestAdditions_5.1.14.iso
  sudo mkdir /media/VBoxGuestAdditions
  sudo mount -o loop,ro /vagrant/Downloads/VBoxGuestAdditions_5.1.14.iso /media/VBoxGuestAdditions
  yes | sudo sh /media/VBoxGuestAdditions/VBoxLinuxAdditions.run
  sudo umount /media/VBoxGuestAdditions
  sudo rmdir /media/VBoxGuestAdditions
SCRIPT

$install_java = <<SCRIPT
  echo "Install Java..."
  sudo add-apt-repository -y ppa:webupd8team/java
  sudo apt-get update
  sudo apt-get -y upgrade
  echo debconf shared/accepted-oracle-license-v1-1 select true | sudo debconf-set-selections
  echo debconf shared/accepted-oracle-license-v1-1 seen true | sudo debconf-set-selections
  sudo apt-get -y install oracle-java8-installer
  sudo apt-get -y install oracle-java8-set-default
SCRIPT

$install_python = <<SCRIPT
  echo "install_python.."
  sudo apt-get update
  sudo apt-get -y install python3
SCRIPT


$install_pycharm = <<SCRIPT
sudo wget https://download.jetbrains.com/python/pycharm-community-2017.1.tar.gz
sudo tar -xvzf pycharm-community-2017.1.tar.gz
sudo cp -R pycharm-community-2017.1 /opt/
cd /opt
sudo chown -R vagrant pycharm-community-2017.1/*
sudo chown -R vagrant pycharm-community-2017.1
SCRIPT

$install_pip = <<SCRIPT
  echo "Install pip..."
  alias python=python3
  sudo apt-get update
  sudo apt-get -y install python3-pip
SCRIPT

$download_and_install_project = <<SCRIPT
echo "Installing the project..."
sudo apt-get update
sudo apt-get install -y wget unzip
cd /srv && wget https://github.com/Myryx/GamingPlatform/archive/master.zip -O /srv/bot.zip 
cd /srv && unzip /srv/bot.zip -d /srv
cd /srv/GamingPlatform-master/src && pip install -r requirements.txt
SCRIPT

Vagrant.configure(2) do |config|

  config.vm.define "KononovYan" do |e|
    # Ubuntu Server 14.04 LTS (Trusty Tahr)
    e.vm.box = "ubuntu/trusty64"
    e.vm.box_url = "https://cloud-images.ubuntu.com/vagrant/trusty/current/trusty-server-cloudimg-amd64-vagrant-disk1.box"
    e.vm.hostname = "ide"
    e.vm.network "forwarded_port", guest: 5432, host: 5431

    e.vm.network "private_network", ip: "192.168.33.100"

    # Create a public network, which generally matched to bridged network.
    # Bridged networks make the machine appear as another physical device on
    # your network.
    # config.vm.network "public_network"

    # Share an additional folder to the guest VM. The first argument is
    # the path on the host to the actual folder. The second argument is
    # the path on the guest to mount the folder. And the optional third
    # argument is a set of non-required options.
    # config.vm.synced_folder "../data", "/vagrant_data"

    # e.vm.synced_folder settings['eclipse']['workspace_host_folder'], "/home/vagrant/workspace"

    e.vm.provider "virtualbox" do |vb|
      vb.gui = true
      vb.memory = "4096"
    end
  end

  config.ssh.shell = "bash -c 'BASH_ENV=/etc/profile exec bash'"
  config.vm.provision "create_downloads_folder", type: "shell", inline: $create_downloads_folder
  config.vm.provision "update_os", type: "shell", inline: $update_os
  # config.vm.provision :reload
  config.vm.provision "create_swap", type: "shell", inline: $create_swap
  config.vm.provision "set_encoding", type: "shell", inline: $set_encoding
  config.vm.provision "install_java", type: "shell", inline: $install_java
  config.vm.provision "install_gui_xfce4", type: "shell", inline: $install_gui_xfce4
  config.vm.provision "autostart_gui_xfce4", type: "shell", inline: $autostart_gui_xfce4
  config.vm.provision "fix_dictionaries", type: "shell", inline: $fix_dictionaries
  config.vm.provision "install_vb_guest_additions", type: "shell", inline: $install_vb_guest_additions
  # config.vm.provision :reload
  config.vm.provision "install_pip", type: "shell", inline: $install_pip
  config.vm.provision "install_python", type: "shell", inline: $install_python
  config.vm.provision "install_pycharm", type: "shell", inline: $install_pycharm
  config.vm.provision "download_and_install_project", type: "shell", inline: $download_and_install_project
  
  
  
end
