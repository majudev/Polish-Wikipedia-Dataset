#!/bin/bash
cd "$(dirname "$0")"

DUMP_DATE=20230120 #yyyy-mm-dd

SHA1SUM="`wget https://dumps.wikimedia.org/plwiki/$DUMP_DATE/plwiki-$DUMP_DATE-sha1sums.txt -O - 2>/dev/null | grep 'plwiki-[0-9]\{8\}-pages-articles-multistream.xml.bz2' | awk '{ print $1 }'`"

if [ ! -e dataset.xml ]; then
	echo "Expecting dataset with sha1sum=$SHA1SUM"
	REAL_SHA1SUM="`shasum dataset.xml.bz2 2>/dev/null | awk '{ print $1 }'`"
	if [ "$REAL_SHA1SUM" != "$SHA1SUM" ]; then
		echo "Got: $REAL_SHA1SUM"
		echo "Downloading compressed dataset pl-$DUMP_DATE"
		wget -c https://dumps.wikimedia.org/plwiki/$DUMP_DATE/plwiki-$DUMP_DATE-pages-articles-multistream.xml.bz2 -O dataset.xml.bz2
	else
		echo "Dataset already downloaded"
		bzip2 -d dataset.xml.bz2
	fi
else
	echo "Dataset already decompressed. To perform decompression again, delete dataset.xml"
fi

echo "XML dataset size: `du -h dataset.xml | awk '{ print $1 }'`B"
