#!/bin/sh

# Create a directory for storing the WikiDumps
DIRNAME=WikiDumps
mkdir -p $DIRNAME

# URL where the enwiki dumps are stored. Dates can change. Do remember to change for latest copy
URL="http://ftp.acc.umu.se/mirror/wikimedia.org/dumps/enwiki/20171103/"
wget -rnH --cut-dirs=100 $URL -P $DIRNAME


# Unzipping the files. It is going to take a lot of time
cd $DIRNAME
for i in *.bz2
do
    bzip2 -d $i &
done

for i in *.7z
do
    p7zip -d $i
done

for i in *.gz
do
    gzip -d $i
done

for i in *.tar.gz
do
    tar -xvf $i
done

echo "Done"

