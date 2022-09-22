import sys
import re
import subprocess
from pythainlp import word_tokenize

class XToZhScorer():
    def isChineseChar(self, uchar):
        """
        :param uchar: input char in unicode
        
        :return: whether the input char is a Chinese character.
        """
        if uchar >= u'\u3400' and uchar <= u'\u4db5':  # CJK Unified Ideographs Extension A, release 3.0
            return True
        elif uchar >= u'\u4e00' and uchar <= u'\u9fa5':  # CJK Unified Ideographs, release 1.1
            return True
        elif uchar >= u'\u9fa6' and uchar <= u'\u9fbb':  # CJK Unified Ideographs, release 4.1
            return True
        elif uchar >= u'\uf900' and uchar <= u'\ufa2d':  # CJK Compatibility Ideographs, release 1.1
            return True
        elif uchar >= u'\ufa30' and uchar <= u'\ufa6a':  # CJK Compatibility Ideographs, release 3.2
            return True
        elif uchar >= u'\ufa70' and uchar <= u'\ufad9':  # CJK Compatibility Ideographs, release 4.1
            return True
        elif uchar >= u'\u20000' and uchar <= u'\u2a6d6':  # CJK Unified Ideographs Extension B, release 3.1
            return True
        elif uchar >= u'\u2f800' and uchar <= u'\u2fa1d':  # CJK Compatibility Supplement, release 3.1
            return True
        elif uchar >= u'\uff00' and uchar <= u'\uffef':  # Full width ASCII, full width of English punctuation, half width Katakana, half wide half width kana, Korean alphabet
            return True
        elif uchar >= u'\u2e80' and uchar <= u'\u2eff':  # CJK Radicals Supplement
            return True
        elif uchar >= u'\u3000' and uchar <= u'\u303f':  # CJK punctuation mark
            return True
        elif uchar >= u'\u31c0' and uchar <= u'\u31ef':  # CJK stroke
            return True
        elif uchar >= u'\u2f00' and uchar <= u'\u2fdf':  # Kangxi Radicals
            return True
        elif uchar >= u'\u2ff0' and uchar <= u'\u2fff':  # Chinese character structure
            return True
        elif uchar >= u'\u3100' and uchar <= u'\u312f':  # Phonetic symbols
            return True
        elif uchar >= u'\u31a0' and uchar <= u'\u31bf':  # Phonetic symbols (Taiwanese and Hakka expansion)
            return True
        elif uchar >= u'\ufe10' and uchar <= u'\ufe1f':
            return True
        elif uchar >= u'\ufe30' and uchar <= u'\ufe4f':
            return True
        elif uchar >= u'\u2600' and uchar <= u'\u26ff':
            return True
        elif uchar >= u'\u2700' and uchar <= u'\u27bf':
            return True
        elif uchar >= u'\u3200' and uchar <= u'\u32ff':
            return True
        elif uchar >= u'\u3300' and uchar <= u'\u33ff':
            return True
        else:
            return False

    def tokenizeString(self, sentence, lc=False):
        """
        :param sentence: input sentence

        :param lc: flag of lowercase. default=False

        :return: tokenized sentence, without the line break "\\n"
        """
    
        #sentence = sentence.decode("utf-8")

        sentence = sentence.strip()

        sentence_in_chars = ""
        for c in sentence:
            if self.isChineseChar(c):
                sentence_in_chars += " "
                sentence_in_chars += c 
                sentence_in_chars += " "
            else:
                sentence_in_chars += c 
        sentence = sentence_in_chars

        if lc:
            sentence = sentence.lower()
        
        # tokenize punctuation
        sentence = re.sub(r'([\{-\~\[-\` -\&\(-\+\:-\@\/])', r' \1 ', sentence)
        
        # tokenize period and comma unless preceded by a digit
        sentence = re.sub(r'([^0-9])([\.,])', r'\1 \2 ', sentence)
        
        # tokenize period and comma unless followed by a digit
        sentence = re.sub(r'([\.,])([^0-9])', r' \1 \2', sentence)
        
        # tokenize dash when preceded by a digit
        sentence = re.sub(r'([0-9])(-)', r'\1 \2 ', sentence)
        
        # one space only between words
        sentence = re.sub(r'\s+', r' ', sentence)
        
        # no leading space    
        sentence = re.sub(r'^\s+', r'', sentence)

        # no trailing space    
        sentence = re.sub(r'\s+$', r'', sentence)

        #sentence += "\n"

        #sentence = sentence.encode("utf-8")

        return sentence

    def tokenizePlainFile(self, inputFile, outputFile):
        """
        :param inputFile: input plain text file
        
        :param outputFile: output plain text file with tokenized text 
        """
        file_r = open(inputFile, 'r')  # input file
        file_w = open(outputFile, 'w')  # result file

        for sentence in file_r:
            new_sentence = self.tokenizeString(sentence)
            file_w.write(new_sentence+'\n')
        
        file_r.close()
        file_w.close()

    def eval(self, route, submit_file, ref_file):
        """
        get bleu score
        """
        ref_tok_file = ref_file + '.tok'
        tok_file = submit_file + '.tok'
        
        self.tokenizePlainFile(submit_file, tok_file)
        self.tokenizePlainFile(ref_file, ref_tok_file)
        rst = subprocess.getoutput('./multi-bleu-detok5.perl ' + ref_tok_file + ' < ' + tok_file)
        bleu_reg = re.compile(r'BLEU = (\d+(\.\d+)?), ')
        mt = bleu_reg.search(rst)
        bleu_score = 0.0
        if mt is not None:
            score = mt.group(1)
            try:
                bleu_score = float(score)
            except:
                bleu_score = 0.0
                
        return bleu_score
     
class ZhToXScorer():
    def token_thai(self, in_file, tok_file):
        fi = open(in_file)
        fo = open(tok_file, 'w')
        for line in fi:
            line = line.strip()
            toks = word_tokenize(line, keep_whitespace=False)
            sent_tok = ' '.join(toks)
            fo.write(sent_tok + '\n')
        fi.close()
        fo.close()    

    def eval(self, route, submit_file, ref_file):
        """
        get bleu score
        """

        if route == "zh_th":
            ref_tok_file = ref_file + '.tok'
            self.token_thai(ref_file, ref_tok_file)
            ref_file = ref_tok_file
            tok_file = submit_file + '.tok'
            self.token_thai(submit_file, tok_file)
            submit_file = tok_file
        
        rst = subprocess.getoutput('./multi-bleu-detok.perl ' + ref_file + ' < ' + submit_file)
        bleu_reg = re.compile(r'BLEU = (\d+(\.\d+)?), ')
        mt = bleu_reg.search(rst)
        bleu_score = 0.0
        if mt is not None:
            score = mt.group(1)
            try:
                bleu_score = float(score)
            except:
                bleu_score = 0.0
                
        return bleu_score    

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('usage: python3 bleu_scorer.py route trans_file ref_file')
        print('--route: choose one in {"fr_zh", "ru_zh", "th_zh","ar_zh", "zh_fr", "zh_fr", "zh_th", "zh_ar"}')
        print('--trans_file: translation file')
        print('--ref_file: reference file')
        exit()
    
    if sys.argv[1] not in {"fr_zh", "ru_zh", "th_zh","ar_zh", "zh_fr", "zh_fr", "zh_th", "zh_ar"}:
        print("Invalid route: " + sys.argv[1] + "!")
        exit()

    if sys.argv[1].endswith("zh"):
        scorer = XToZhScorer()
    else:
        scorer = ZhToXScorer()
    print("bleu score:", scorer.eval(sys.argv[1], sys.argv[2], sys.argv[3]))
