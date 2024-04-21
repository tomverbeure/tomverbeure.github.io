#~/projects/fake_parallel_printer/fake_printer.py -i -p /dev/ttyACM0 -f r3273_ -s pcl -v

gpcl6 -dNOPAUSE -sOutputFile=r3273_tmp.png -sDEVICE=png256 -g4000x4000 -r600x600 r3273_0.pcl
convert r3273_tmp.png -filter box -resize 1000 r3273_filt.png
#rm r3273_tmp.png
convert r3273_filt.png -crop 640x480+315+94 r3273.png
#rm r3273_filt.png

