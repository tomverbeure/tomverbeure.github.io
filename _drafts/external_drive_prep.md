# Prepare an External USB Backup Drive 

**You can skip this section if you use an internal backup drive.**

If you want to use an external USB drive for backup, it needs to be
partitioned and formatted separately. Here's how to do this with the
old-school command line method.

In the instructions below, I'm using a 500GB SSD that I had laying around.

* Open a separate terminal window, and start `dmesg -w`.
* Plug the drive into the t520.
* You should seem something like this in the `dmesg` terminal:

    ```
[ 1589.224571] usb 4-1: new SuperSpeed Gen 1 USB device number 3 using xhci_hcd
[ 1589.251148] usb 4-1: New USB device found, idVendor=174c, idProduct=55aa, bcdDevice= 1.00
[ 1589.251158] usb 4-1: New USB device strings: Mfr=2, Product=3, SerialNumber=1
[ 1589.251163] usb 4-1: Product: U32M
[ 1589.251168] usb 4-1: Manufacturer: MiniPro
[ 1589.251172] usb 4-1: SerialNumber: 123456789082
[ 1589.259208] usb 4-1: UAS is blacklisted for this device, using usb-storage instead
[ 1589.259217] usb-storage 4-1:1.0: USB Mass Storage device detected
[ 1589.266024] usb-storage 4-1:1.0: Quirks match for vid 174c pid 55aa: 400000
[ 1589.266102] scsi host2: usb-storage 4-1:1.0
[ 1590.285708] scsi 2:0:0:0: Direct-Access     MiniPro  U32M             0    PQ: 0 ANSI: 6
[ 1590.286998] sd 2:0:0:0: Attached scsi generic sg1 type 0
[ 1590.292270] sd 2:0:0:0: [sdb] Spinning up disk...
[ 1591.308393] ..ready
[ 1592.333112] sd 2:0:0:0: [sdb] 976773168 512-byte logical blocks: (500 GB/466 GiB)
[ 1592.333711] sd 2:0:0:0: [sdb] Write Protect is off
[ 1592.333720] sd 2:0:0:0: [sdb] Mode Sense: 43 00 00 00
[ 1592.334752] sd 2:0:0:0: [sdb] Write cache: enabled, read cache: enabled, doesn't support DPO or FUA
[ 1592.355794]  sdb: sdb1
[ 1592.359859] sd 2:0:0:0: [sdb] Attached SCSI disk
    ```

* Use `fdisk` to create a single backup partition

    **The instructions below will destroy all the previous contents on the drive!!!**

    In the text below, all lines with `<<<<<<<<` contain commands that are 
    entered by the user.

    ```sh
sudo fdisk /dev/sdb                             <<<<<<<<
    ```

    ```
Command (m for help): n                         <<<<<<<<
Partition type
   p   primary (0 primary, 0 extended, 4 free)
   e   extended (container for logical partitions)
Select (default p): p                           <<<<<<<<
Partition number (1-4, default 1):              <<<<<<<<
First sector (2048-976773167, default 2048):    <<<<<<<<
Last sector, +/-sectors or +/-size{K,M,G,T,P} (2048-976773167, default 976773167):

Created a new partition 1 of type 'Linux' and of size 465.8 GiB.
    ```

Command (m for help): p                         <<<<<<<<

Disk /dev/sdb: 465.78 GiB, 500107862016 bytes, 976773168 sectors
Disk model: U32M
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disklabel type: dos
Disk identifier: 0x00000000

Device     Boot Start       End   Sectors   Size Id Type
/dev/sdb1        2048 976773167 976771120 465.8G 83 Linux

Command (m for help): w                         <<<<<<<<
The partition table has been altered.
Calling ioctl() to re-read partition table.
Syncing disks.
    ```

* Format an EXT4 partition

    I always use EXT4 for my Linux partitions. Use whatever you prefer.

    ```sh
sudo mkfs.ext4 /dev/sdb1
    ```

* Create a mount point for the backup partition

    I mount the timemachine partition to `/mnt/timemachine`. You can obviously
    whichever location you prefer.

    ```sh
sudo mkdir -p /mnt/timemachine
    ```

* Get the partition UUID

    On my machine, the newly created partition is known as `/dev/sdb1`, but
    if you plug in other drives, this assignment might change.  To make sure that 
    this partition always gets mounted to the right location in the filesystem, I select 
    the partition by its UUID value instead.

    You can find the partion UUID value like this:

    ```sh
ls -als /dev/disk/by-uuid/                           
    ```

    ```
total 0
drwxr-xr-x 2 root root 100 Jun 19 21:44 ./
drwxr-xr-x 7 root root 140 Jun 19 21:06 ../
lrwxrwxrwx 1 root root  10 Jun 19 21:23 33DE-451A -> ../../sda1
lrwxrwxrwx 1 root root  10 Jun 19 21:23 50e204d8-341a-4359-835f-5d769a26edeb -> ../../sda2
lrwxrwxrwx 1 root root  10 Jun 19 21:44 e18cd28d-29fd-4691-b162-d3898d4b0637 -> ../../sdb1
    ```

* Update `/etc/fstab` to add the backup partition

    ```sh
sudo vi /etc/fstab
    ```
    
    Add the following line at the bottom the `/etc/fstab` file:
    
    ```
# Timemachine storage
UUID=e18cd28d-29fd-4691-b162-d3898d4b0637 /mnt/timemachine auto defaults 0 0
    ```

    The UUID code is the one that you found in the previous step.

* Mount the backup partition

    ```sh
sudo mount -av
    ```

    ```
/                        : ignored
/boot/efi                : already mounted
none                     : ignored
/mnt/timemachine         : successfully mounted
    ```
