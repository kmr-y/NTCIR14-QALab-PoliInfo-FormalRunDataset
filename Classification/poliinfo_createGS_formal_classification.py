#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""NTCIR-14 QA Lab PoliInfo ClassificationタスクのGSデータ作成スクリプト（Formal Run版）．
1　3人が一致したsupport/againstをつけた場合support/against、それ以外other
2　2人が（以下略）
3　1人が（以下略）
4　作業者AをGSDとした場合
5　作業者Bを（以下略）
6　作業者Cを（以下略）
7　support/againstをつけた数がスコア
このうち，4〜6はGSがすでに存在するので，このスクリプトでは作成対象外とする．

更新：2018.11.19
作成者：乙武 北斗
"""

import sys
import argparse
import json
import math
from collections import Counter
from pathlib import Path
from typing import List, Dict, Tuple


def get_args():
    parser = argparse.ArgumentParser(
        description="""NTCIR-14 QA Lab PoliInfo ClassificationタスクのGSデータ作成スクリプト（Formal Run版）．""")

    parser.add_argument('-i', '--input-gs-files',
                        nargs='+',
                        required=True,
                        help='ベースとなるGSデータをすべて指定する')

    return parser.parse_args()


def load_gs(files: List[str]) -> Tuple[List[dict], Dict[str, Dict[str, dict]]]:
    """
    2つの値を返す：
    [0]: 出力値以外の要素を持ったインスタンスを出現順に記録したリスト
    [1]: IDをキーとして，出力値を各アノテーターごとに記録したdict
    """
    l = []
    gs_map = {}
    for i, file in enumerate(files):
        p = Path(file)
        annotator = p.stem.split('-')[-1]
        with open(file) as f:
            json_array = json.load(f)

        for ins in json_array:
            # 最初のGSからは出力値以外を抽出して記録しておく
            if i == 0:
                l.append({
                    'ID': ins['ID'],
                    'Topic': ins['Topic'],
                    'Utterance': ins['Utterance']
                })

            idstr = ins['ID'].split('-')[-1]
            if idstr not in gs_map:
                gs_map[idstr] = {}
            gs_map[idstr][annotator] = {
                'Relevance': ins['Relevance'],
                'Fact-checkability': ins['Fact-checkability'],
                'Stance': ins['Stance'],
                'Class': ins['Class']
            }

    return l, gs_map


def main():
    args = get_args()

    # GS読み込み
    gs_list, gs_map = load_gs(args.input_gs_files)
    num = len(gs_list)

    print('[')
    for i, ins in enumerate(gs_list):
        idstr = ins['ID'].split('-')[-1]
        
        d_m = {
            'Relevance': {k: v['Relevance'] for k, v in gs_map[idstr].items()},
            'Fact-checkability': {k: v['Fact-checkability'] for k, v in gs_map[idstr].items()},
            'Stance': {k: v['Stance'] for k, v in gs_map[idstr].items()},
            'Class': {k: v['Class'] for k, v in gs_map[idstr].items()}
        }

        print(json.dumps(dict(d_m, **ins), ensure_ascii=False), end='')
        print(',') if i < num - 1 else print('')
    
    print(']')


if __name__ == '__main__':
    main()
