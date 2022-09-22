# 初赛log

## 文件组织

    # 原始数据
    - datasets
        - evaluation
    # 预训练模型   
    - mbart.cc25.v2
    # now using
    - raw
    - .
      - clean.py (清洗数据)
      - multi_cut.py(中泰分词，abondon)
      - prepare.sh(切分翻译两种语言文段)
      - tospm.py(sentencepiece)
      - train_data_split.py(切分train / valid)

## how to start

### first score 
#### fr-zh train-valid

``` shell

    sh prepare.sh  ## todo 包含run.sh之前处理

    python3 clean ## todo

    cd raw/fr-zh

    python ../../train_data_spilit.py fr zh /data/ecoli/ikcest/raw/fr-zh/fr-zh.train.clean /data/ecoli/ikcest/raw/fr-zh/data 2000

    python ../../train_data_spilit.py fr zh /data/ecoli/ikcest/raw/fr-zh/fr-zh.train.clean /data/ecoli/ikcest/raw/fr-zh/data 2000 

    mkdir bpe

    python ../../tospm.py ../../mbart.cc25.v2/sentence.bpe.model < data/train.fr  > bpe/train.bpe.fr

    python ../../tospm.py ../../mbart.cc25.v2/sentence.bpe.model < data/dev.fr  > bpe/valid.bpe.fr

    python ../../tospm.py ../../mbart.cc25.v2/sentence.bpe.model < data/dev.zh  > bpe/valid.bpe.zh

    python ../../tospm.py ../../mbart.cc25.v2/sentence.bpe.model < data/train.zh  > bpe/train.bpe.zh

    fairseq-preprocess   --source-lang fr_XX   --target-lang zh_CN   --trainpref train.bpe   --validpref valid.bpe    --destdir /data/ecoli/ikcest/raw/data-bin-withtest   --thresholdtgt 0   --thresholdsrc 0   --srcdict /data/ecoli/ikcest/mbart.cc25.v2/dict.txt   --tgtdict /data/ecoli/ikcest/mbart.cc25.v2/dict.txt   --workers 40 ## todo:如何跑test

    sh run.sh  ## todo: 修改

    langs=ar_AR,cs_CZ,de_DE,en_XX,es_XX,et_EE,fi_FI,fr_XX,gu_IN,hi_IN,it_IT,ja_XX,kk_KZ,ko_KR,lt_LT,lv_LV,my_MM,ne_NP,nl_XX,ro_RO,ru_RU,si_LK,tr_TR,vi_VN,zh_CN

    PYTHONIOENCODING=utf-8  fairseq-generate /data/ecoli/ikcest/raw/fr-zh/data-bin-fix   --path /data/ecoli/ikcest/raw/fr-zh/9_11_t2/checkpoint_best.pt   --task translation_from_pretrained_bart   --gen-subset test   -t zh_CN -s fr_XX   --bpe 'sentencepiece' --sentencepiece-model /data/ecoli/ikcest/mbart.cc25.v2/sentence.bpe.model   --remove-bpe 'sentencepiece'   --langs $langs > te2.all

    cat te2.all | grep -P "^H" |sort -V |cut -f 3- | sed 's/\[fr_XX\]//g' > t2.hyp

    sacrebleu  -tok zh  raw/fr-zh/data/dev.zh < t2.hyp > t2.score

    ---------生成test----------
    cat bpe/test.zh | fairseq-interactive data-bin/  --path 9_12/checkpoint_best.pt  --bpe 'sentencepiece' --sentencepiece-model /data/ecoli/ikcest/mbart.cc25.v2/sentence.bpe.model   --remove-bpe 'sentencepiece' --task translation_from_pretrained_bart --langs $langs | tee test.out 

    cat test.out | grep -P "^H" |sort -V |cut -f 3- | sed 's/\[fr_XX\]//g' > fr-zh.rst


```

#### t2.score

{
 "name": "BLEU",
 "score": 34.5,
 "signature": "nrefs:1|case:mixed|eff:no|tok:zh|smooth:exp|version:2.1.0",
 "verbose_score": "67.4/43.8/29.4/20.5 (BP = 0.944 ratio = 0.946 hyp_len = 53431 ref_len = 56493)",
 "nrefs": "1",
 "case": "mixed",
 "eff": "no",
 "tok": "zh",
 "smooth": "exp",
 "version": "2.1.0"
}


## 脚本参数说明

todo