#!/bin/bash

#prepare mbart
ROOT=/data/ecoli/ikcest

if [! -d "/mbart.cc25.v2"];then
wget https://dl.fbaipublicfiles.com/fairseq/models/mbart/mbart.cc25.v2.tar.gz
tar -xf mbart.cc25.v2.tar.gz
fi

PATHTOMBART=$ROOT/mbart.cc25.v2

raw=$ROOT/raw
datasets=$ROOT/datasets
#cut the train date#
mkdir raw
for lang in fr ru th;
do
mkdir $raw/$lang'-zh'

cut -f 1 $datasets/$lang'_zh.train' > $raw/$lang'-zh'/$lang'-zh'.train.$lang
cut -f 2 $datasets/$lang'_zh.train' > $raw/$lang'-zh'/$lang'-zh'.train.zh
cp ./datasets/$lang'_zh.test' raw/$lang'-zh'/

mkdir $raw/'zh-'$lang
cut -f 1 $datasets/'zh_'$lang'.train' > $raw/'zh-'$lang/'zh-'$lang.train.zh
cut -f 2 $datasets/'zh_'$lang'.train' > $raw/'zh-'$lang/'zh-'$lang.train.$lang
cp ./datasets/'zh_'$lang.test raw/'zh-'$lang/
done

# clean (Only discard overly long items)
for lang  in fr ru th;
do
python ./clean $raw/$lang'-zh' lang zh train
python ./clean $raw/'zh-'$lang zh lang train
done


TOSPM=$ROOT/TOSPM.py
SPILIT=$ROOT/train_data_spilit.py
# spilit and bpe
for lang in fr ru th;
do
cd $raw/'zh-'$lang
python $SPILIT zh $lang $raw/'zh-'$lang/'zh-'$lang.train.clean \
$raw/'zh-'$lang/data 2000

mkdir bpe 

python $TOSPM $PATHTOMBART/sentence.bpe.model \
< data/train.$lang  > bpe/train.bpe.$lang

python $TOSPM $PATHTOMBART/sentence.bpe.model \
< data/dev.$lang  > bpe/valid.bpe.$lang

python $TOSPM $PATHTOMBART/sentence.bpe.model \
< data/dev.zh  > bpe/valid.bpe.zh

python $TOSPM $PATHTOMBART/sentence.bpe.model \
< data/train.zh  > bpe/train.bpe.zh


cd $raw/$lang'-zh'
python $SPILIT $lang zh $raw/$lang'-zh'/$lang'-zh'.train.clean \
$raw/$lang'-zh'/data 2000

mkdir bpe 

python $TOSPM $PATHTOMBART/sentence.bpe.model \
< data/train.$lang  > bpe/train.bpe.$lang

python $TOSPM $PATHTOMBART/sentence.bpe.model \
< data/dev.$lang  > bpe/valid.bpe.$lang

python $TOSPM $PATHTOMBART/sentence.bpe.model \
< data/dev.zh  > bpe/valid.bpe.zh

python $TOSPM $PATHTOMBART/sentence.bpe.model \
< data/train.zh  > bpe/train.bpe.zh

done 


# # split train and dev #
# split=$ROOT/train_data_spilit.py
# for lang in fr ru th;
# do
# python $split $lang zh $raw/$lang'-zh'/$lang'-zh'.train $raw/$lang'-zh'/ 2000
# python $split zh $lang $raw/'zh-'$lang/'zh-'$lang.train $raw/'zh-'$lang/ 2000
# done
