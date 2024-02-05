
~/tools/ghostpcl-10.0.0-linux-x86_64/gpcl6-1000-linux-x86_64 -dNOPAUSE -sOutputFile=test.png -sDEVICE=png256 -g8000x8000 -r600x600 $1.pcl
convert test.png -filter point -resize 2000  test2.png
convert test2.png -crop 640x480+315+94 $1.png
