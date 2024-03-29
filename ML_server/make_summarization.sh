#!/bin/sh
echo $2 > making.txt
bash get_video.sh $1
name=""
tmp="tmp/*"
for filename in $tmp; do
    name=("$filename")
done
name=${name##*/}
name=${name%.*}
if [ ! -f "./tmp/$name.wav" ]; then
    echo " " > making.txt
    return 0
fi
echo "get comment"
max=10
for ((i=0; i < $max; i++)); do
    python -B -c "import get_comment; import sys; get_comment.get_comment_json(sys.argv[1],sys.argv[2])" $2 "tmp/$name.json"
    if [ -f "./tmp/$name.json" ]; then
        break
    fi
done
if [ -f "tmp/$name.json" ] && [ -f "tmp/$name.wav" ] ; then
    echo "$1,$name" >> name_list.csv
    python speech_segmentation.py "$name"
    python make_data.py "$name"
    python predict.py "$name"
    python summarization_by_comment_count_and_bert.py "$name" $2
else
    echo $2 >> error.txt
fi
rm -rf "./tmp/$name.wav"
rm -rf "./tmp/$name.csv"
rm -rf "./tmp/$name.json"
rm -rf "./data/$name.csv"
rm -rf "./predict_result/$name.csv"
echo " " > making.txt
if [ -f "summarization_by_comment_count_and_bert/$2.csv" ]; then
    python send_data.py "$2"
fi
