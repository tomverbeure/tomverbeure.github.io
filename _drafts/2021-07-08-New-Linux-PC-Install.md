---
layout: post
title: New Linux PC Install
date:  2021-12-19 00:00:00 -1000
categories:
---


```
sudo apt update
sudo apt upgrade

sudo apt install curl git g++ flex bison clang gperf htop feh pinta vim-gtk3 autoconf libtool libusb-dev libzip-dev doxygen libpython3-all-dev
cmake gettext python3-numpy python3-setuptools libboost-dev \

sudo apt install build-essential \
libreadline-dev gawk tcl-dev libffi-dev git \
graphviz xdot pkg-config python3 libboost-system-dev \
libboost-python-dev libboost-filesystem-dev zlib1g-dev

sudo apt install gtkwave bundler

sudo apt install openssh-server
sudo systemctl status ssh
sudo ufw allow ssh


# Kicad
sudo add-apt-repository --yes ppa:kicad/kicad-5.1-releases
sudo apt install --install-recommends kicad

# Verilator
mkdir ~/tools
cd ~/tools
git clone https://github.com/verilator/verilator.git
cd verilator
autoconf
./configure --prefix=/opt/verilator
make -j$(nproc)
sudo make install 

# iverilog
cd ~/tools
git clone https://github.com/steveicarus/iverilog.git
cd iverilog
autoconf
./configure --prefix=/opt/iverilog
make -j$(nproc)
sudo make install 

# Yosys
cd ~/tools
git clone https://github.com/YosysHQ/yosys.git
cd yosys
make config-clang
echo 'PREFIX := /opt/yosys' >> Makefile.conf
make -j$(nproc)
sudo make install

# SpinalHDL
sudo add-apt-repository -y ppa:openjdk-r/ppa
sudo apt-get update
sudo apt install openjdk-8-jdk
sudo update-alternatives --config java
sudo update-alternatives --config javac

# Also install SBT: see SpinalHDL README.md

# RISC-V Toolchain
curl https://static.dev.sifive.com/dev-tools/freedom-tools/v2020.12/riscv64-unknown-elf-toolchain-10.2.0-2020.12.8-x86_64-linux-ubuntu14.tar.gz > ~/Downloads/riscv64-unknown-elf-toolchain-10.2.0-2020.12.8-x86_64-linux-ubuntu14.tar.gz
sudo tar xfvz ~/Downloads/riscv64-unknown-elf-toolchain-10.2.0-2020.12.8-x86_64-linux-ubuntu14.tar.gz
sudo chmod 755 /opt/riscv64-unknown-elf-toolchain-10.2.0-2020.12.8-x86_64-linux-ubuntu14/

```

