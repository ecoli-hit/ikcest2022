#!/bin/bash

sl="fr_XX"
tl="zh_CN"

if [ "$1" = "fr" ]
then
    sl="fr_XX"
elif [ "$1" = "zh" ]
then
    sl="zh_CN"
elif [ "$1" = "ru" ]
then
    sl="ru_RU"
elif [ "$1" = "th" ]
then
    sl="th_TH"
else
    echo "wrong"
    exit 1
fi

if [ "$2" = "fr" ]
then
    tl="fr_XX"
elif [ "$2" = "zh" ]
then
    tl="zh_CN"
elif [ "$2" = "ru" ]
then
    tl="ru_RU"
elif [ "$2" = "th" ]
then
    tl="th_TH"
else
    echo "wrong"
    exit 1
fi

cd raw
cd $1-$2

python ../../clean.py /data/ecoli/ikcest/raw/$1-$2/ $1-$2.train.$1 $1-$2.train.$2 train 


mv $1-$2.train.$1.clean $1-$2.train.clean.$1
mv $1-$2.train.$2.clean $1-$2.train.clean.$2

python ../../train_data_spilit.py $1 $2 /data/ecoli/ikcest/raw/$1-$2/$1-$2.train.clean /data/ecoli/ikcest/raw/$1-$2/data-nc 2000

mkdir bpe-nc

python ../../tospm.py ../../mbart.cc25.v2/sentence.bpe.model < data-nc/train.$1  > bpe-nc/train.bpe.$sl

python ../../tospm.py ../../mbart.cc25.v2/sentence.bpe.model < data-nc/train.$2  > bpe-nc/train.bpe.$tl

python ../../tospm.py ../../mbart.cc25.v2/sentence.bpe.model < data-nc/dev.$2  > bpe-nc/valid.bpe.$tl

python ../../tospm.py ../../mbart.cc25.v2/sentence.bpe.model < data-nc/dev.$1  > bpe-nc/valid.bpe.$sl

python ../../tospm.py ../../mbart.cc25.v2/sentence.bpe.model < $1_$2.test  > bpe-nc/test.$1


cd bpe-nc/

fairseq-preprocess   --source-lang $sl   --target-lang $tl   --trainpref train.bpe   --validpref valid.bpe    \
    --destdir /data/ecoli/ikcest/raw/data-bin-withtest   \
    --thresholdtgt 0   --thresholdsrc 0   \
    --srcdict /data/ecoli/ikcest/mbart.cc25.v2/dict.txt   \
    --tgtdict /data/ecoli/ikcest/mbart.cc25.v2/dict.txt   --workers 40