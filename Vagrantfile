# -*- mode: ruby -*-
# vi: set ft=ruby :
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "base"
  config.vm.provider "virtualbox" do |v|
    v.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
    v.customize ["modifyvm", :id, "--natdnsproxy1", "on"]
    v.customize ["modifyvm", :id, "--memory", 2048]
  end
  config.ssh.forward_x11 = true

$_apt_get = <<ENDAPT
sudo apt-get update
sudo apt-get install -y flex bison qtcreator qtcreator-doc cmake libicu-dev 
sudo apt-get install -y python-qscintilla2 libgeos-dev libgdal1-dev zip
sudo apt-get install -y python-sip-dev python-qt4-dev python-qt4 uicilibris 
sudo apt-get install -y pyqt4-dev-tools libgsl0-dev git-core txt2tags grass-dev
sudo apt-get install -y python-qwt5-qt4 libspatialindex-dev python-gdal
sudo apt-get install -y libqscintilla2-dev python-psycopg2 python-sphinx
ENDAPT

$_bash_login = <<ENDLOGIN
echo -e "cd /vagrant" >> /home/vagrant/.bash_login
echo -e "source ~/.bashrc" >> /home/vagrant/.bash_login
ENDLOGIN

  config.vm.provision :shell, :inline => $_apt_get
  config.vm.provision :shell, :inline => $_bash_login

end
