~/projects/fake_parallel_printer/fake_printer.py -i -p /dev/ttyACM0 -f hp54542a_ -s thinkjet.pcl -v
gpcl6 -dNOPAUSE -sOutputFile=hp54542a.png -sDEVICE=png256 -g680x700 -r75x75 hp54542a_0.thinkjet.pcl
convert hp54542a.png -crop 640x364+19+96 hp54542a.crop.png
