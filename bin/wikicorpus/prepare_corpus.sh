#!/bin/sh

usage()
{
    echo 'Usage: prepare_corpus.sh -w <WikiExtractor path> -d <Wikidumps path> -o <Output file>'
    exit
}
ARGS="$@"
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

echo "$WIKIEXRACT_PATH $WIKIDUMPS_PATH $OUTPUT_PATH here"
#sh parse_wikidumps_json.sh -w "$WIKIEXRACT_PATH" -d "$WIKIDUMPS_PATH" -o "$OUTPUT_PATH"
sh parse_wikidumps_json.sh $ARGS
python get_wikipedia_content.py --input_dir $OUTPUT_PATH --output_file corpus.txt

echo "Done"

