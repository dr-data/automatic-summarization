#!/bin/sh


usage()
{
    echo 'Usage: parse_wikidumps_json.sh -w <WikiExtractor path> -d <Wikidumps path> -o <Output file>'
    exit
}

echo "$@ , $#"
if [ "$#" -ne 6 ];
then
    usage
fi

WIKIEXRACT_PATH=""
WIKIDUMPS_PATH=""
OUTPUT_PATH=""

count=0
while [ $count -le "$#" ]:
do
    case $1 in
        -w)
            WIKIEXTRACT_PATH="$2"
            shift 2
            ;;
        -d)
            WIKIDUMPS_PATH="$2"
            shift 2
            ;;
        -o)
            OUTPUT_PATH="$2"
            shift 2
            ;;
        *)
            break
            ;;
    esac
    count=`expr $count + 1`
done

echo "Check $WIKIEXTRACT_PATH, $WIKIDUMPS_PATH, $OUTPUT_PATH"

if [ ! -f $WIKIEXTRACT_PATH/WikiExtractor.py ];
then
    echo "WikiExtractor not present, cloning the repository $WIKIEXTRACT_PATH"
    git clone https://github.com/attardi/wikiextractor.git $WIKIEXTRACT_PATH

fi

for f in $WIKIDUMPS_PATH/*.xml
do
    echo "$f"
    echo "python $WIKIEXTRACT_PATH/WikiExtractor.py -o $OUTPUT_PATH -s --json --processes 10 $WIKIDUMPS_PATH$f"
    python $WIKIEXTRACT_PATH/WikiExtractor.py -o $OUTPUT_PATH -s --json --processes 10 $f &
done
