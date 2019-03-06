#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""NTCIR-14 QA Lab PoliInfo Segmentationタスク（Formal Run）の自動評価スクリプト

更新：2018.11.14
作成者：乙武 北斗
"""

import sys
import argparse
import json
import pathlib
import math
from collections import Counter
from typing import Tuple, Dict


def get_args():
    parser = argparse.ArgumentParser(
        description="""NTCIR-14 QA Lab PoliInfo Segmentationタスクの自動評価スクリプトです．""")

    parser.add_argument('-i', '--input-files',
                        nargs='+',
                        required=True,
                        help='評価対象のJSONファイルを指定します')

    parser.add_argument('-g', '--gs-data',
                        required=True,
                        help='GSデータを指定します'
                        )

    parser.add_argument('-o', '--output-dir',
                        required=True,
                        help='個別評価結果の出力ディレクトリを指定します'
                        )

    return parser.parse_args()


def load_gs(path) -> Dict[str, Tuple[int, int, int, int]]:
    gs = {}
    with open(path) as f:
        gs = json.load(f)

    gs_map = {}  # type: Dict[str, Tuple[int, int, int, int]]
    for ins in gs:
        i = ins['ID'].split('-')[-1]
        gs_map[i] = (int(ins['QuestionStartingLine']), int(ins['QuestionEndingLine']), int(ins['AnswerStartingLine']),
                     int(ins['AnswerEndingLine']))
    return gs_map


def main():
    args = get_args()

    # GS読み込み
    gs_map = load_gs(args.gs_data)
    headers = ['Group ID', 'Priority', 'Recall', 'Precision', 'Q-Recall', 'Q-Precision', 'A-Recall', 'A-Precision',
               'lines', 'output', 'match', 'Q-lines', 'Q-output', 'Q-match', 'A-lines', 'A-output', 'A-match']
    print('\t'.join(headers))

    # 評価データ各々に対して
    for path in args.input_files:
        filename_split = pathlib.Path(path).stem.split('_', 1)
        task = 'Segmentation'
        run_type = filename_split[0].split('-')[-1]
        tmp = filename_split[1].rsplit('-', 1)
        team_name = tmp[0]
        priority = tmp[1]

        ## RecallとPrecisionのもと
        nums_line = Counter()
        nums_output = Counter()
        nums_match = Counter()

        # 個別評価結果出力先
        output_path = pathlib.Path(args.output_dir) / pathlib.Path('Result-{0}.txt'.format(pathlib.Path(path).stem))

        # JSON読み込み
        with open(path) as f, open(output_path, mode='w') as f2:
            rheaders = ['ID', 'Precision', 'Recall',
                        'Q-解答', 'Q-正解', 'Q-一致', 'Q-Precision', 'Q-Recall',
                        'A-解答', 'A-正解', 'A-一致', 'A-Precision', 'A-Recall']
            print('\t'.join(rheaders), file=f2)
            for ins in json.load(f):
                i = ins['ID'].split('-')[-1]
                qstart = int(ins['QuestionStartingLine'])
                qend = int(ins['QuestionEndingLine'])
                astart = int(ins['AnswerStartingLine'])
                aend = int(ins['AnswerEndingLine'])

                qoutput_lines = set(range(qstart, qend + 1))
                qcorrect_lines = set(range(gs_map[i][0], gs_map[i][1] + 1))
                aoutput_lines = set(range(astart, aend + 1))
                acorrect_lines = set(range(gs_map[i][2], gs_map[i][3] + 1))

                res = {
                    'ID': ins['ID'],
                    'Precision': (len(acorrect_lines & aoutput_lines) + len(qcorrect_lines & qoutput_lines)) / (
                            len(aoutput_lines) + len(qoutput_lines)),
                    'Recall': (len(acorrect_lines & aoutput_lines) + len(qcorrect_lines & qoutput_lines)) / (
                            len(acorrect_lines) + len(qcorrect_lines)),
                    'Q-解答': '{0}-{1}'.format(qstart, qend),
                    'Q-正解': '{0}-{1}'.format(gs_map[i][0], gs_map[i][1]),
                    'Q-一致': len(qcorrect_lines & qoutput_lines),
                    'Q-Precision': len(qcorrect_lines & qoutput_lines) / len(qoutput_lines) if len(
                        qoutput_lines) > 0 else math.nan,
                    'Q-Recall': len(qcorrect_lines & qoutput_lines) / len(qcorrect_lines),
                    'A-解答': '{0}-{1}'.format(astart, aend),
                    'A-正解': '{0}-{1}'.format(gs_map[i][2], gs_map[i][3]),
                    'A-一致': len(acorrect_lines & aoutput_lines),
                    'A-Precision': len(acorrect_lines & aoutput_lines) / len(aoutput_lines) if len(
                        aoutput_lines) > 0 else math.nan,
                    'A-Recall': len(acorrect_lines & aoutput_lines) / len(acorrect_lines)
                }

                nums_line['S'] += (len(acorrect_lines) + len(qcorrect_lines))
                nums_line['Q'] += len(qcorrect_lines)
                nums_line['A'] += len(acorrect_lines)
                nums_output['S'] += (len(aoutput_lines) + len(qoutput_lines))
                nums_output['Q'] += len(qoutput_lines)
                nums_output['A'] += len(aoutput_lines)
                nums_match['S'] += (len(acorrect_lines & aoutput_lines) + len(qcorrect_lines & qoutput_lines))
                nums_match['Q'] += len(qcorrect_lines & qoutput_lines)
                nums_match['A'] += len(acorrect_lines & aoutput_lines)

                print('\t'.join([str(res[k]) for k in rheaders]), file=f2)

            # マイクロ平均
            res = {
                'ID': 'マイクロ平均',
                'Precision': nums_match['S'] / nums_output['S'],
                'Recall': nums_match['S'] / nums_line['S'],
                'Q-解答': nums_output['Q'],
                'Q-正解': nums_line['Q'],
                'Q-一致': nums_match['Q'],
                'Q-Precision': nums_match['Q'] / nums_output['Q'],
                'Q-Recall': nums_match['Q'] / nums_line['Q'],
                'A-解答': nums_output['A'],
                'A-正解': nums_line['A'],
                'A-一致': nums_match['A'],
                'A-Precision': nums_match['A'] / nums_output['A'],
                'A-Recall': nums_match['A'] / nums_line['A'],
            }
            print('\t'.join([str(res[k]) for k in rheaders]), file=f2)

        # 全体結果
        res = {
            'Group ID': team_name,
            'Priority': priority,
            'Recall': nums_match['S'] / nums_line['S'],
            'Precision': nums_match['S'] / nums_output['S'],
            'Q-Recall': nums_match['Q'] / nums_line['Q'],
            'Q-Precision': nums_match['Q'] / nums_output['Q'],
            'A-Recall': nums_match['A'] / nums_line['A'],
            'A-Precision': nums_match['A'] / nums_output['A'],
            'lines': nums_line['S'],
            'output': nums_output['S'],
            'match': nums_match['S'],
            'Q-lines': nums_line['Q'],
            'Q-output': nums_output['Q'],
            'Q-match': nums_match['Q'],
            'A-lines': nums_line['A'],
            'A-output': nums_output['A'],
            'A-match': nums_match['A']
        }

        print('\t'.join([str(res[k]) for k in headers]))


if __name__ == '__main__':
    main()
