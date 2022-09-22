#!/bin/bash

declare -A site
site["fr"]="fr_XX"
site["ru"]="ru_RU"
site["th"]="th_TH"

ROOT=/data/ecoli/ikcest
PATHTOMBART=$ROOT/mbart.cc25.v2
raw=$ROOT/raw


for lang in fr ru th;
do

cd $raw/$lang'-zh'/bpe
fairseq-preprocess   --source-lang ${site[$lang]}  --target-lang zh_CN   \
--trainpref train.bpe   --validpref valid.bpe    --destdir $raw/data-bin   \
--thresholdtgt 0   --thresholdsrc 0   \
--srcdict PATHTOMBART/dict.txt   \
--tgtdict PATHTOMBART/dict.txt   \
--workers 40

cd $raw/'zh-'$lang/bpe
fairseq-preprocess   --source-lang zh_CN  --target-lang ${site[$lang]}   \
--trainpref train.bpe   --validpref valid.bpe    --destdir $raw/data-bin   \
--thresholdtgt 0   --thresholdsrc 0   \
--srcdict PATHTOMBART/dict.txt   \
--tgtdict PATHTOMBART/dict.txt   \
--workers 40

done
echo ${site["runoob"]}