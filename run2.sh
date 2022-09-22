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

ROOT=/data/ecoli/ikcest
DATA=$ROOT/raw/$1-$2/data-bin-nc
PRETRAIN=$ROOT/mbart.cc25.v2/model.pt
OUTPUT=$ROOT/raw/$1-$2/9_14_nc
langs=ar_AR,cs_CZ,de_DE,en_XX,es_XX,et_EE,fi_FI,fr_XX,gu_IN,hi_IN,it_IT,ja_XX,kk_KZ,ko_KR,lt_LT,lv_LV,my_MM,ne_NP,nl_XX,ro_RO,ru_RU,si_LK,tr_TR,vi_VN,zh_CN
mkdir $OUTPUT
touch $OUTPUT/train.log

CUDA_VISIBLE_DEVICES=0,1,2,3 fairseq-train $DATA \
--encoder-normalize-before --decoder-normalize-before  --share-all-embeddings \
--arch mbart_large --task translation_from_pretrained_bart  --source-lang $sl --target-lang $tl \
--criterion label_smoothed_cross_entropy --label-smoothing 0.2  \
--dataset-impl mmap --optimizer adam --adam-eps 1e-06 --adam-betas '(0.9, 0.98)' \
--lr-scheduler polynomial_decay --lr 3e-05 --min-lr -1 \
--warmup-updates 2500 --total-num-update 10000 --max-update 10000  \
--dropout 0.3 --attention-dropout 0.1 --weight-decay 0.0 \
--max-tokens 4096 --update-freq 2 --save-interval 1 --save-interval-updates 5000 --keep-interval-updates 1 --no-epoch-checkpoints \
--log-format simple --log-interval 1000 --reset-optimizer --reset-meters --reset-dataloader --reset-lr-scheduler \
--restore-file $PRETRAIN --langs $langs --layernorm-embedding  --ddp-backend no_c10d --fp16 \
--seed 222 --save-dir $OUTPUT \
| tee $OUTPUT/train.log

