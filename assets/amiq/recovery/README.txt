This package contains the following files:

* AMIQ_recovery-4.00.tar.gz

  An archive created by R&S with PDF files and the data for the PREPARE-1.4 and 
  PROGRAM recovery floppy disks.

  The Pdsum14.img file is a 1.44 MB floppy image for the PREPARE disk.

  The Amiq400.dat file is a regular with the AMIQ 4.00 software. Upon closer
  inspection, you'll notice that Amiq400.dat is a ZIP file that can be opened
  with any zip decompression tool.

  When a floppy is inserted in the AMIQ, the AUTOEXEC.BAT checks for the presence
  of any Amiq*.dat files and, when present, first does a file integrity check and
  then copies all files straight into the file system.

  The archive also has a "Diskcopy" tool that can be used to copy the Pdsum14.img
  file to a floppy, though I haven't tested it.

* AMIQ-program-4.00.img.gz

  An 1.44MB floppy image that contains the Amiq400.dat file.

  I created this image because my floppy emulator needs an image instead of a file.

