from pyexpat import model
from statistics import mode
import sys
import pdb
import pprint
import logging
import os
import random

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils import data
import numpy as np
import tqdm.auto as tqdm
from pathlib import Path
from argparse import Namespace
from fairseq import utils

import matplotlib.pyplot as plt

import re

# data_dir = 'Data'
# prefix = Path(data_dir).absolute()
# prefix.mkdir(parents=True, exist_ok=True)

# src_lang = 'fr'
# tgt_lang = 'zh'

# data_prefix = f'{prefix}/train_valid'
# test_prefix = f'{prefix}/test'
dataset_raw_prefix = '/data/ecoli/ikcest/raw'


def strQ2B(ustring):
    # 中文特殊符号的转化
    # 全角符号转半角符号
    ss = []
    for s in ustring:
        rstring = ""
        for uchar in s:
            inside_code = ord(uchar)
            if inside_code == 12288:  # Full width space: direct conversion
                inside_code = 32
            elif (inside_code >= 65281 and inside_code <= 65374):  # Full width chars (except space) conversion
                inside_code -= 65248
            rstring += chr(inside_code)
        ss.append(rstring)
    return ''.join(ss)


def clean_s(s, lang):
    if lang == 'zh' or lang == 'th':
        s = strQ2B(s)
        # s = re.sub(r"\([^()]*\)", "", s)        # 去除()内的内容
        s = s.replace('（', '(')
        s = s.replace('）', ')')
        s = s.replace(' ', '')
        s = s.replace('-', '')
        s = s.replace('“', '"')
        s = s.replace('”', '"')
        s = s.replace('_', '')
        s = re.sub('([。,;!?()\"~「」])', r' \1 ', s)  # 在标点符号前加空格

    # 不是很懂其他语言的标点,因此这里是用了英语的标点清洗
    else:
        s = strQ2B(s)
        # s = re.sub(r"\([^()]*\)", "", s)
        s = s.replace('-', '')
        s = re.sub('([.,;!?()\"])', r' \1 ', s)

    s = ' '.join(s.strip().split())
    return s

# 其他语言的长度怎么算的,其实我这里也不太明白,暂时先用英语的表示来显示长度吧
def len_s(s, lang):
    if lang == 'zh':
        return len(s)
    elif lang == 'fr':
        return len(s.split())

def clean_corpus(prefix, l1, l2, model='train',ratio=5, max_len=200, min_len=1):
    #**
    # prefix 目标文件路径前缀
    # l1/l2 相对raw文件的待清洗文件路径
    # model 清洗方式*#
    if Path(f'{prefix}/{l1}.clean').exists() and Path(f'{prefix}/{l2}.clean').exists():
        print(f'{prefix}/{l1}.clean & {prefix}/{l2}.clean exists. skipping clean.')
        return

    else:
        if model == 'train':
            l1_in_path = f'{prefix}/{l1}-{l2}.train.{l1}'
            l2_in_path = f'{prefix}/{l1}-{l2}.train.{l2}'
            with open(l1_in_path, 'r', encoding='utf8') as l1_in_f:
                with open(l2_in_path, 'r', encoding='utf8') as l2_in_f:
                    with open(f'{prefix}/{l1}-{l2}.train.clean.{l1}', 'w', encoding='utf8') as l1_out_f:
                        with open(f'{prefix}/{l1}-{l2}.train.clean.{l2}', 'w', encoding='utf8') as l2_out_f:
                            for s1 in l1_in_f:
                                s1 = s1.strip()
                                # s1 = clean_s(s1, 'fr')
                                s1_len = len_s(s1, 'fr')
                                print(s1)

                                s2 = l2_in_f.readline().strip()
                                # s2 = clean_s(s2, 'zh')
                                s2_len = len_s(s2, 'zh')

                                if s1_len < min_len or s2_len < min_len:
                                    continue
                                if s1_len > max_len or s2_len > max_len:
                                    continue
                                if s1_len/s2_len > ratio or s2_len/s1_len > ratio:
                                    continue

                                print(s1, file=l1_out_f)
                                print(s2, file=l2_out_f)
        elif model == 'test':
            with open(f'{prefix}/{l1}_{l2}.test', 'r', encoding='utf8') as test_in_f:
                with open(f'{prefix}/{l1}.clean.test', 'w', encoding='utf8') as test_out_f:
                    for s in test_in_f:
                        s = s.strip()
                        s = clean_s(s, l1)
                        print(s, file=test_out_f)


if __name__ == '__main__':
    ##
    # prefix : 路径前缀
    # l1 : src lang
    # l2 : tat lang
    # model : trian or test（目前不支持test 因为还没改）#
    prefix = sys.argv[1]
    l1 = sys.argv[2]
    l2 = sys.argv[3]
    model = sys.argv[4]
    clean_corpus(prefix,l1,l2,model)
    