#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""NTCIR-14 QA Lab PoliInfo Classificationタスクの自動評価スクリプト（Formal Run版）
1　3人が一致したsupport/againstをつけた場合support/against、それ以外other
2　2人が（以下略）
3　1人が（以下略）
4　各作業者をGSDとした場合
5　support/againstをつけた数がスコア

更新：2018.11.26
作成者：乙武 北斗
"""

import sys
import argparse
import json
import math
import fileinput
from pprint import pprint
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple, Set, Union


def get_args():
    parser = argparse.ArgumentParser(
        description="""NTCIR-14 QA Lab PoliInfo Classificationタスク Formal Runの自動評価スクリプトです．実行は単一トピックで行ってください．""")

    parser.add_argument('-i', '--input-files',
                        nargs='+',
                        required=True,
                        help='評価対象のJSONファイルをすべて指定します')

    parser.add_argument('-a', '--gs-file',
                        required=True,
                        help='GSデータを指定します（createGSスクリプトで作成したもの）'
                        )

    parser.add_argument('-o', '--output-dir',
                        required=True,
                        help='個別評価結果の出力ディレクトリを指定します'
                        )

    return parser.parse_args()


def load_gs(gs_file: str) -> Tuple[Dict[str, Dict[str, Dict[str, int]]], List[str]]:
    """
    dict[ID][LABEL][annotator]形式でGSを取得, annotatorリストも返す
    """
    labels = [('Relevance', 'Rl'), ('Fact-checkability', 'FC'), ('Stance', 'St'), ('Class', 'Cl')]
    gs_map = {}
    annotators = set()
    with open(gs_file) as f:
        json_array = json.load(f)

    for ins in json_array:
        idstr = ins['ID'].split('-')[-1]
        gs_map[idstr] = {label: ins[full_label] for full_label, label in labels}
        for a in ins['Class'].keys():
            annotators.add(a)

    return gs_map, list(annotators)


def get_correct(gs_map: Dict[str, Dict[str, Dict[str, int]]], idstr: str, label: str, method: str) -> Union[
    Set[int], Dict[int, int]]:
    """
    GSマップから指定したID,LABEL,評価方法の正解セットを生成する．
    """
    vmap = gs_map[idstr][label]
    if method == 'N1':
        return {v for v in vmap.values()}
    elif method == 'N2':
        c = Counter(vmap.values())
        return {k for k, v in c.items() if v >= 2}
    elif method == 'N3':
        c = Counter(vmap.values())
        return {k for k, v in c.items() if v >= 3}
    elif method == 'SC':
        return Counter(vmap.values())


def load_inputs(files: List[str]) -> Dict[str, Dict[str, Tuple[str, List[dict]]]]:
    """
    dict[team][priority][idx]形式でinputsを取得
    """
    input_map = {}
    for file in files:
        p = Path(file)
        filename_split = p.stem.split('_', 1)
        tmp = filename_split[1].split('-')
        team_name = '-'.join(tmp[:-1])
        priority = tmp[-1]

        if team_name not in input_map:
            input_map[team_name] = {}
        input_map[team_name][priority] = (p.stem, [])

        with open(file) as f:
            try:
                json_array = json.load(f)
            except json.JSONDecodeError as e:
                print(file, file=sys.stderr)
                print('全体のフォーマットにエラーがあるため，JSONの各行読み込みを試します．', file=sys.stderr)
                json_array = []
                for line in fileinput.input(file):  # type: str
                    if not (line.startswith('[') or line.startswith(']')):
                        json_array.append(json.loads(line))

        for ins in json_array:
            try:
                idstr = ins['ID'].split('-')[-1]
                input_map[team_name][priority][1].append({
                    'ID': idstr,
                    'Rl': int(ins['Relevance']) if ins['Relevance'] is not None else None,
                    'FC': int(ins['Fact-checkability']) if ins['Fact-checkability'] is not None else None,
                    'St': int(ins['Stance']) if ins['Stance'] is not None else None,
                    'Cl': int(ins['Class']) if ins['Class'] is not None else None,
                    'Topic': ins['Topic']
                })
            except:
                print(file, file=sys.stderr)
                print(ins, file=sys.stderr)
                sys.exit(1)

    return input_map


def main():
    args = get_args()

    # GS読み込み
    gs_map, annotators = load_gs(args.gs_file)

    # 評価データ読み込み
    input_map = load_inputs(args.input_files)

    methods = ['N1', 'N2', 'N3', 'SC']
    labels = ['Rl', 'FC', 'St', 'Cl']
    headers = ['Group ID', 'Priority']
    for label in labels:
        if label in {'St', 'Cl'}:
            ms = ['Acc', 'P0', 'P1', 'P2', 'R0', 'R1', 'R2']
        else:
            ms = ['Acc', 'P0', 'P1', 'R0', 'R1']
        for m in ms:
            for ann in annotators:
                headers.append('{0}_{1}_{2}'.format(ann, label, m))
            for mm in methods:
                headers.append('{0}_{1}_{2}'.format(mm, label, m))
    print('\t'.join(headers))

    # 評価データ各々に対して
    for team in input_map.keys():
        for priority in input_map[team].keys():
            basefilename, ins_list = input_map[team][priority]

            # 混同行列 cm[annotator][label][val]
            cm: Dict[str, Dict[str, Dict[int, Counter]]] = {}
            for k in annotators + methods:
                cm[k] = {}
                for l in labels:
                    if l in {'St', 'Cl'}:
                        cm[k][l] = {0: Counter(), 1: Counter(), 2: Counter()}
                    else:
                        cm[k][l] = {0: Counter(), 1: Counter()}

            # 個別評価結果出力先
            output_path1 = Path(args.output_dir) / Path('Result-{0}.txt'.format(basefilename))
            output_path2 = Path(args.output_dir) / Path('ConfusionMatrix-{0}.txt'.format(basefilename))

            with output_path1.open(mode='w') as f2, output_path2.open(mode='w') as f3:
                rheaders = ['ID']
                for label in labels:
                    rheaders.append('解答'.format(label))
                    rheaders.extend(['正解{0}_{1}'.format(label, k) for k in annotators + methods])
                print('\t'.join(rheaders), file=f2)

                # 各インスタンス
                for ins in ins_list:
                    ins_results = []

                    # もしGSに含まれていないIDがInstanceに存在する場合はスキップする
                    if ins['ID'] not in gs_map:
                        print('{0}-{1} ID: {2} はGSに存在しません'.format(team, priority, ins['ID']), file=sys.stderr)
                        continue

                    # 各ラベル
                    for label in labels:
                        ins_results.append(str(ins[label]))

                        # 各アノテータGS
                        for ann in annotators:
                            gs_crr = gs_map[ins['ID']][label][ann]
                            cm[ann][label][gs_crr][ins[label]] += 1
                            ins_results.append(str(gs_map[ins['ID']][label][ann]))

                        # N1-N3: アノテータn人がつけていた値を正解とする
                        for mm in ['N1', 'N2', 'N3']:
                            crrset: Set[int] = get_correct(gs_map, ins['ID'], label, mm)
                            if len(crrset) > 0:
                                crrval = int(''.join([str(v) for v in sorted(crrset, reverse=True)]))
                                ins_results.append(','.join([str(v) for v in sorted(crrset, reverse=True)]))
                                if crrval not in cm[mm][label]:
                                    cm[mm][label][crrval] = Counter()
                                cm[mm][label][crrval][ins[label]] += 1
                            else:
                                ins_results.append('-')
                                if 9 not in cm[mm][label]:
                                    cm[mm][label][9] = Counter()
                                cm[mm][label][9][ins[label]] += 1

                        # SC: アノテータがつけていた値の数をスコアにする
                        crrmap: Dict[int, int] = get_correct(gs_map, ins['ID'], label, 'SC')
                        ins_results.append(
                            ','.join([str(k) for k in sorted(gs_map[ins['ID']][label].values(), reverse=True)]))
                        if ins[label] in crrmap:
                            cm['SC'][label][ins[label]][ins[label]] += crrmap[ins[label]]
                            for k, v in crrmap.items():
                                if k != ins[label]:
                                    cm['SC'][label][k][ins[label]] += v
                        else:
                            for k, v in crrmap.items():
                                cm['SC'][label][k][ins[label]] += v

                    # 個別結果出力
                    print('{0}\t{1}'.format(ins['ID'], '\t'.join(ins_results)), file=f2)

                # Confusion Matrix出力
                for l in labels:
                    print('{0}:'.format(l), file=f3)
                    for k in annotators + methods:
                        # print(sum([list(c.keys()) for c in cm[k][l].values()], []), file=sys.stderr)
                        # print('{0}:{1}\t{2}:{3}'.format(team, priority, l, k), file=sys.stderr)
                        # pprint(cm[k][l], stream=sys.stderr)

                        outputs = sorted(set(sum([list(c.keys()) for c in cm[k][l].values()], [])),
                                         key=lambda x: x if x is not None else 999)
                        outputs_str = [str(x) for x in outputs]
                        print('正解{0} ＼ 出力\t{1}'.format(k, '\t'.join(outputs_str)), file=f3)
                        for crr in sorted(cm[k][l].keys()):
                            outputs2 = [str(cm[k][l][crr][i]) for i in outputs]
                            print('{0}\t{1}'.format(crr if crr != 9 else '-', '\t'.join(outputs2)), file=f3)
                        print('', file=f3)
                    print('=======================', file=f3)

            # Precision/Recall
            row = [team, priority]
            for l in labels:
                if l in {'St', 'Cl'}:
                    ms = ['Acc', 'P0', 'P1', 'P2', 'R0', 'R1', 'R2']
                else:
                    ms = ['Acc', 'P0', 'P1', 'R0', 'R1']
                for m in ms:
                    for k in annotators + methods:
                        cmx = cm[k][l]
                        if m == 'Acc':
                            crr = 0
                            for c in [x for x in cmx.keys() if x != 9]:
                                if c < 10:
                                    crr += cmx[c][c]
                                else:
                                    crrset = {int(nc) for nc in str(c)}
                                    for est in cmx[c].keys():
                                        if est in crrset:
                                            crr += cmx[c][est]
                            accuracy = crr / sum([sum(vv.values()) for kk, vv in cmx.items() if kk != 9])
                            row.append(str(accuracy))
                        elif m.startswith('P'):
                            tc = int(m[1])
                            tmp = sum([vv[tc] for kk, vv in cmx.items() if kk != 9])
                            tmp2 = cmx[tc][tc]
                            if tc == 0:
                                tmp2 += cmx.get(10, {0: 0})[0] + cmx.get(20, {0: 0})[0]
                            elif tc == 1:
                                tmp2 += cmx.get(10, {1: 0})[1]
                            elif tc == 2:
                                tmp2 += cmx.get(20, {2: 0})[2]
                            precision = tmp2 / tmp if tmp > 0 else math.nan
                            row.append(str(precision))
                        elif m.startswith('R'):
                            tc = int(m[1])
                            div = sum(cmx[tc].values())
                            tmp = cmx[tc][tc]
                            if tc == 0:
                                div += sum(cmx.get(10, {0: 0}).values()) + sum(cmx.get(20, {0: 0}).values())
                                tmp += cmx.get(10, {0: 0})[0] + cmx.get(20, {0: 0})[0]
                            elif tc == 1:
                                div += sum(cmx.get(10, {0: 0}).values())
                                tmp += cmx.get(10, {1: 0})[1]
                            elif tc == 2:
                                div += sum(cmx.get(20, {0: 0}).values())
                                tmp += cmx.get(20, {2: 0})[2]
                            recall = tmp / div if div > 0 else math.nan
                            row.append(str(recall))

            print('\t'.join(row))


if __name__ == '__main__':
    main()
