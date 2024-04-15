~/projects/gpib_talk_dump/gpib_talk_to_file.py 11 tds540.thinkjet.pcl
gpcl6 -dNOPAUSE -sOutputFile=tds540.png -sDEVICE=png256 -g680x574 -r75x75 tds540.thinkjet.pcl
convert tds540.png -crop 640x480+20+47 tds540.crop.png
