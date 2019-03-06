#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""NTCIR-14 QA Lab PoliInfo SummarizationタスクのROUGE自動評価スクリプト．
動作要件として，以下のモジュールが必要です．
・mecab-python3

更新：2018.08.17
作成者：乙武 北斗
"""

import sys
import argparse
import json
import pathlib
import MeCab
import re
import math
from collections import defaultdict
from rouge.pythonrouge import Pythonrouge
from typing import Dict, Tuple, Optional, TypeVar, List
from tqdm import tqdm

T = TypeVar('T')

functional_verbs = {"為る", "居る", "成る", "有る"}
content_words = ["助詞", "助動詞", "感動詞", "空白", "補助記号", "記号-一般"]
adverbial_nouns = {"所", "為", "くらい"}
formal_nouns = {"の", "事", "物", "積り", "訳"}
numeral_notation1_regex = re.compile(r'([^兆億万]+兆)?([^兆億万]+億)?([^兆億万]+万)?([^兆億万]*)')
numeral_notation2_regex = re.compile(r'([^千百十]*千)?([^千百十]*百)?([^千百十]*十)?([^千百十]*)')


def nonEmpty(s: str) -> bool:
    return s is not None and s != ''


def isEmpty(s: str) -> bool:
    return not nonEmpty(s)


def or_else(n: Optional[T], e: T) -> T:
    return n if n is not None else e


def is_content_word(pos: str) -> bool:
    for el in content_words:
        if pos.startswith(el):
            return False
    return True


def is_noun(pos: str, original: str) -> bool:
    return (pos.startswith('名詞') or pos == "記号-文字" or pos.startswith(
        "接尾辞-名詞的") or pos == "接頭辞") and (original not in adverbial_nouns) and (original not in formal_nouns)


def is_numeral(pos: str) -> bool:
    return pos == '名詞-数詞'


def get_args():
    parser = argparse.ArgumentParser(
        description="""NTCIR-14 QA Lab PoliInfo SummarizationタスクのROUGE自動評価スクリプトです．
        動作要件として，mecab-python3モジュールが必要です．""")

    parser.add_argument('-i', '--input-files',
                        nargs='+',
                        required=True,
                        help='評価対象のJSONファイルを指定します')

    parser.add_argument('-g', '--gs-data',
                        required=True,
                        help='GSデータを指定します'
                        )

    parser.add_argument('-d', '--unidic-path',
                        required=True,
                        help='MeCabで用いるUnidicのパスを指定します'
                        )

    parser.add_argument('-o', '--output-dir',
                        required=True,
                        help='個別評価結果の出力ディレクトリを指定します'
                        )

    return parser.parse_args()


def load_gs(path: str) -> Dict[str, Tuple[int, str]]:
    pat = re.compile(r'(\d+)字以内')
    gs = {}
    with open(path) as f:
        gs = json.load(f)

    gs_map = {}  # type: Dict[str, Tuple[int, str]]
    for ins in gs:
        i = ins['ID'].split('-')[-1]
        gs_map[i] = (int(pat.match(ins['Length']).group(1)), ins['Summary'])
    return gs_map


def word2ids(summary: List[str], reference: List[str]) -> Tuple[List[List[str]], List[List[List[str]]]]:
    id_dict = defaultdict(lambda: len(id_dict))
    rsummary = [[' '.join([str(id_dict[w]) for w in summary])]]
    rreference = [[[' '.join([str(id_dict[w]) for w in reference])]]]
    # summary = [[' '.join([str(id_dict[w]) for w in sent.split()])
    #             for sent in doc] for doc in summary]
    # reference = [[[' '.join([str(id_dict[w]) for w in sent.split()])
    #                for sent in doc] for doc in refs] for refs in reference]
    return rsummary, rreference


def replace_all_kanji_to_arabic(numerals: str) -> str:
    tmp = numerals.replace("一", "1").replace("二", "2").replace("三", "3").replace("四", "4").replace("五", "5").replace(
        "六", "6").replace("七", "7").replace("八", "8").replace("九", "9").replace("〇", "0")
    tmp = re.sub(r'[^0123456789]', '', tmp)
    tmp = re.sub(r'^0+', '', tmp)
    return tmp


def parse_kanji_numerals(kanji_numerals: str) -> Optional[int]:
    def p3(numerals: str, has_default: bool) -> Optional[int]:
        if nonEmpty(numerals):
            if has_default:
                return 1
            else:
                return None
        try:
            return int(replace_all_kanji_to_arabic(numerals))
        except Exception as err:
            print(err, file=sys.stderr)
            return None

    def p4(numerals: str) -> Optional[int]:
        numeral_array = list(reversed(replace_all_kanji_to_arabic(numerals)))
        num = 0
        for i, x in enumerate(numeral_array):
            try:
                num += int(int(x) * math.pow(10, i))
            except:
                pass
        return num

    def p2(numerals: str) -> Optional[int]:
        if isEmpty(numerals):
            return None
        mobj = numeral_notation2_regex.match(numerals)
        if mobj is not None:
            if nonEmpty(mobj.group(1)) and nonEmpty(mobj.group(2)) and nonEmpty(mobj.group(3)):
                base2 = 10
                print(numerals, file=sys.stderr)
                output2 = or_else(p3(mobj.group(1)[:-1], True), 0) * base2 * base2 * base2 + or_else(
                    p3(mobj.group(2)[:-1], True), 0) * base2 * base2 + or_else(p3(mobj.group(3)[:-1], True),
                                                                               0) * base2 + or_else(
                    p3(mobj.group(4), False), 0)
                return output2
            else:
                return p4(numerals)
        else:
            return None

    tmp = kanji_numerals.replace('ゼロ-zero', '〇').replace('零', '〇')
    matchObj = numeral_notation1_regex.match(tmp)
    if matchObj is not None:
        base = 10000
        default_string = 'a'
        output = or_else(p2(or_else(matchObj.group(1), default_string)[:-1]), 0) * base * base * base + or_else(
            p2(or_else(matchObj.group(2), default_string)[:-1]), 0) * base * base + or_else(
            p2(or_else(matchObj.group(3), default_string)[:-1]), 0) * base + or_else(p2(matchObj.group(4)), 0)
        return output
    else:
        return None


def extract_words(mecab, s: str) -> List[str]:
    parsed = mecab.parse(s)
    ret = []
    compound_nouns = []
    numerals = []

    def append(term):
        if term not in functional_verbs:
            ret.append(term)

    def extract_compound_noun():
        if len(compound_nouns) > 0:
            append(''.join(compound_nouns))
            compound_nouns.clear()

    def extractNumeral():
        if len(numerals) > 0:
            x = parse_kanji_numerals(''.join(numerals))
            if x is not None:
                compound_nouns.append(str(x))
            numerals.clear()

    def compound_noun(tokens: List[str]):
        if len(tokens) < 5:
            return

        pos = tokens[4]

        def buffer_noun():
            compound_nouns.append(tokens[3].strip())

        def buffer_numeral():
            numerals.append(tokens[3].strip())

        def extract_content_word():
            if is_content_word(pos):
                append(tokens[3].strip())

        if is_noun(pos, tokens[0]):
            if is_numeral(pos):
                buffer_numeral()
            else:
                extractNumeral()
                buffer_noun()
        else:
            extractNumeral()
            extract_compound_noun()
            extract_content_word()

    for line in filter(lambda x: x != 'EOS', parsed.splitlines()):
        tmp = line.split('\t')
        if len(tmp) > 1:
            compound_noun(tmp)
        else:
            append(tmp[0])

    extractNumeral()
    extract_compound_noun()

    return ret


def extract_all_words(mecab, s: str, is_original: bool) -> List[str]:
    parsed = mecab.parse(s)
    idx = 0 if is_original else 3
    ret = []

    def append(term):
        ret.append(term)

    for line in filter(lambda x: x != 'EOS', parsed.splitlines()):
        tmp = line.split('\t')
        if len(tmp) > 2:
            append(tmp[idx])
        else:
            append(tmp[0])
    return ret


def main():
    args = get_args()
    mecab = MeCab.Tagger('-d {0}'.format(args.unidic_path))

    # 語のとり方
    extract_types = ['内容語', '短単位（原形）', '短単位（表層形）']

    # ROUGEスコア種別
    rouge_types = ['ROUGE-1', 'ROUGE-2', 'ROUGE-3', 'ROUGE-4', 'ROUGE-L', 'ROUGE-SU4', 'ROUGE-W-1.2']

    # GS読み込み
    gs_map = load_gs(args.gs_data)
    # print('Group ID\tPriority\t有効回答率\t平均ROUGEスコア（有効回答）\t平均ROUGEスコア（トータル）')
    print('\t'.join(['Group ID', 'Priority', '有効回答率', '\t'.join(
        ['平均{0}-{1}_{2}（有効回答）'.format(rt, st, et) for st in ['R', 'F'] for et in extract_types for rt in
         rouge_types]), '\t'.join(
        ['平均{0}-{1}_{2}（トータル）'.format(rt, st, et) for st in ['R', 'F'] for et in extract_types for rt in
         rouge_types])]))

    # 評価データ各々に対して
    for path in tqdm(args.input_files):
        filename_split = pathlib.Path(path).stem.split('_', 1)
        task = 'Summarization'
        run_type = filename_split[0].split('-')[-1]
        tmp = filename_split[1].split('-')
        team_name = '-'.join(tmp[:-1])
        priority = tmp[-1]

        # 統計情報
        nums = 0
        avails = 0
        score_sums_a = [
            defaultdict(float), defaultdict(float), defaultdict(float)
        ]
        score_sums_t = [
            defaultdict(float), defaultdict(float), defaultdict(float)
        ]

        # 個別評価結果出力先
        output_path = pathlib.Path(args.output_dir) / pathlib.Path('Result-{0}.txt'.format(pathlib.Path(path).stem))

        # JSON読み込み
        print('open: {0}'.format(path), file=sys.stderr)
        with open(path) as f, output_path.open(mode='w') as f2:
            # 個別結果出力ヘッダ
            print('\t'.join(['ID', '制限字数', '解答字数', '有効解答', '\t'.join(
                ['{0}-{1}_{2}'.format(rt, st, et) for st in ['R', 'F'] for et in extract_types for rt in
                 rouge_types])]), file=f2)
            for ins in json.load(f):
                i = ins['ID'].split('-')[-1]
                summary = ins['Summary']
                max_len, reference = gs_map[i]
                extracted_summaries = [
                    extract_words(mecab, summary),
                    extract_all_words(mecab, summary, False),
                    extract_all_words(mecab, summary, True)
                ]
                extracted_references = [
                    extract_words(mecab, reference),
                    extract_all_words(mecab, reference, False),
                    extract_all_words(mecab, reference, True)
                ]
                w2is = [
                    word2ids(extracted_summaries[0], extracted_references[0]),
                    word2ids(extracted_summaries[1], extracted_references[1]),
                    word2ids(extracted_summaries[2], extracted_references[2])
                ]
                rouges = []
                for j in range(len(w2is)):
                    rouges.append(Pythonrouge(summary_file_exist=False,
                                              summary=w2is[j][0], reference=w2is[j][1],
                                              n_gram=4, ROUGE_SU4=True, ROUGE_L=True, ROUGE_W=True))
                scores = [rouge.calc_score() for rouge in rouges]

                nums += 1
                if len(summary) <= max_len:
                    avails += 1
                    for j in range(len(w2is)):
                        for k in scores[j].keys():
                            score_sums_a[j][k] += scores[j][k]
                for j in range(len(w2is)):
                    for k in scores[j].keys():
                        score_sums_t[j][k] += scores[j][k]

                # 個別結果出力
                print('\t'.join([ins['ID'], str(max_len), str(len(summary)), '1' if len(summary) <= max_len else '0',
                                 '\t'.join(
                                     ['{0}'.format(scores[j]['{0}-{1}'.format(rt, st)]) for st in ['R', 'F'] for j in
                                      range(len(w2is)) for rt in rouge_types])]), file=f2)

        # 全体結果
        print('\t'.join([team_name, priority, str(avails / nums), '\t'.join(
            ['{0}'.format(score_sums_a[j]['{0}-{1}'.format(rt, st)] / avails) for st in ['R', 'F'] for j in
             range(len(extract_types)) for rt in
             rouge_types]), '\t'.join(
            ['{0}'.format(score_sums_a[j]['{0}-{1}'.format(rt, st)] / nums) for st in ['R', 'F'] for j in
             range(len(extract_types)) for rt in
             rouge_types])]))


if __name__ == '__main__':
    main()
