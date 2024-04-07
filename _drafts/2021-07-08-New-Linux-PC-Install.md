---
layout: post
title: New Linux PC Install
date:  2021-12-19 00:00:00 -1000
categories:
---


# Vim
~/.vimrc:
```
set visualbell
```

# Focus

Tweak application -> Windows -> Focus on Hover

# General packages
```
sudo apt update
sudo apt upgrade

sudo apt install git vim-gtk3
sudo apt install curl g++ flex bison clang gperf htop feh pinta autoconf \
libtool libusb-dev libzip-dev doxygen libpython3-all-dev \
cmake gettext python3-numpy python3-setuptools libboost-dev build-essential \
libreadline-dev gawk tcl-dev libffi-dev git \
graphviz xdot pkg-config python3 libboost-system-dev \
libboost-python-dev libboost-filesystem-dev zlib1g-dev \
help2man gnome-tweaks imagemagick libfftw3-dev libxaw7-dev 

sudo apt install gtkwave bundler
```

# Git settings

```
git config --global user.name "Tom Verbeure"
git config --global user.email "hombre+github.com@gmail.com"
mkdir -p ~/.git/config
touch ~/.git/config/ignore
```

Global ignore file: ~/.config/git/ignore

# ssh remote login
```
sudo apt install openssh-server
sudo systemctl status ssh
sudo ufw allow ssh
```

# Kicad
```
sudo add-apt-repository --yes ppa:kicad/kicad-8.0-releases
sudo apt update
sudo apt install --install-recommends kicad
```

# Install rvm
```
gpg --keyserver keyserver.ubuntu.com --recv-keys 409B6B1796C275462A1703113804BB82D39DC0E3 7D2BAF1CF37B13E2069D6956105BD0E739499BDB
sudo apt install software-properties-common
sudo apt-add-repository -y ppa:rael-gc/rvm
sudo apt-get update
sudo apt-get install rvm
sudo usermod -a -G rvm $USER
rvm fix-permissions system
rvm fix-permissions user
**reboot before doing anyting more with rvm**

# rvm 2.7 for blog: https://blog.francium.tech/setting-up-ruby-2-7-6-on-ubuntu-22-04-fdb9560715f7
rvm pkg install openssl
 #rvm install 2.7.6 --with-openssl-dir=$HOME/.rvm/usr
rvm install 2.7.6 --with-openssl-dir=/usr/share/rvm/usr
```

# Verilator
```
mkdir -p ~/tools
cd ~/tools
git clone https://github.com/verilator/verilator.git
cd verilator
autoconf
./configure --prefix=/opt/verilator
make -j$(nproc)
sudo make install 
```

# iverilog

```
mkdir -p ~/tools
cd ~/tools
git clone https://github.com/steveicarus/iverilog.git
cd iverilog
autoconf
./configure --prefix=/opt/iverilog
make -j$(nproc)
sudo make install 
```

# Yosys

```
mkdir -p ~/tools
cd ~/tools
git clone https://github.com/YosysHQ/yosys.git
cd yosys
make config-clang
echo 'PREFIX := /opt/yosys' >> Makefile.conf
make -j$(nproc)
sudo make install
```

# SpinalHDL

```
sudo add-apt-repository -y ppa:openjdk-r/ppa
sudo apt-get update
sudo apt install openjdk-8-jdk
sudo update-alternatives --config java
sudo update-alternatives --config javac

# Also install SBT: see SpinalHDL README.md
```

# RISC-V Toolchain

Download `riscv64-elf-ubuntu-22.04-gcc-nightly-2024.03.01-nightly.tar.gz` from here: https://github.com/riscv-collab/riscv-gnu-toolchain/releases

```
cd /opt
sudo tar xfvz ~/Downloads/riscv64-elf-ubuntu-22.04-gcc-nightly-2024.03.01-nightly.tar.gz
sudo mv riscv riscv64-unknown-elf
sudo chmod -R og-w ./riscv64-unknown-elf/
```

Old:
```
curl https://static.dev.sifive.com/dev-tools/freedom-tools/v2020.12/riscv64-unknown-elf-toolchain-10.2.0-2020.12.8-x86_64-linux-ubuntu14.tar.gz > ~/Downloads/riscv64-unknown-elf-toolchain-10.2.0-2020.12.8-x86_64-linux-ubuntu14.tar.gz
sudo tar xfvz ~/Downloads/riscv64-unknown-elf-toolchain-10.2.0-2020.12.8-x86_64-linux-ubuntu14.tar.gz
sudo chmod 755 /opt/riscv64-unknown-elf-toolchain-10.2.0-2020.12.8-x86_64-linux-ubuntu14/
```

# CUDA
```
***FIRST REMOVE ANYTHING RELATED TO NVIDIA**
sudo apt-get remove --purge '^nvidia-.*'
sudo apt-get remove --purge '^libnvidia-.*'
sudo apt-get remove --purge '^cuda-.*'

sudo apt install nvidia-driver-530 (or later)
**Reboot otherwise nvidia-smi doesn't work**
sudo apt install nvidia-cuda-toolkit nvidia-cuda-toolkit-doc
```

# ngspice
download ngspice tarball

```
cd ~/tools
tar xfv <tarball>
cd ngspice-40
mkdir -p release
cd release
../configure  --with-x --enable-xspice --enable-cider --enable-openmp --with-readline=yes --disable-debug --prefix=/opt/ngspice
make -j $(nproc)
```

