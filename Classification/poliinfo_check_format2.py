#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""NTCIR-14 QA Lab PoliInfoタスクのOutputとなるJSONファイルの書式チェックを行うプログラム．
Formal Runフォーマット修正版．

更新：2018.09.28
作成者：乙武 北斗
"""

import sys
import argparse
import fileinput
import json


id_fields = {
    'seg': {'ID'},
    'sum': {'ID'},
    'cls': {'ID'}
}

output_fields = {
    'seg': {'QuestionStartingLine', 'QuestionEndingLine', 'AnswerStartingLine', 'AnswerEndingLine'},
    'sum': {'Summary'},
    'cls': {'Relevance', 'Fact-checkability', 'Stance', 'Class'}
}


def construct_dict(pairs):
    assert len(pairs) == len(set(pair[0]
                                 for pair in pairs)), '同名のフィールドが複数存在します．'
    return dict(pairs)


def get_args():
    parser = argparse.ArgumentParser(description="""NTCIR-14 QA Lab PoliInfoタスクのOutputとなるJSONファイルの書式チェックを行います．
    タスクを[-t|--type]オプションにて指定の上，ご利用ください．""")

    # 標準入力がない場合は，ファイル指定必須
    if sys.stdin.isatty():
        parser.add_argument('json_file', help='対象JSONファイル（指定しない場合は標準入力から読み込みます）')

    parser.add_argument('-t', '--type',
                        choices=['seg', 'sum', 'cls'],
                        nargs=1,
                        required=True,
                        help='対象ファイルの種別を指定します(seg:Segmentation, sum:Summarization, cls:Classification)')

    return parser.parse_args()


def main():
    args = get_args()

    # JSON読み込み
    src = '-' if not hasattr(args, 'json_file') else args.json_file
    lines = [line.rstrip() for line in fileinput.input(
        src, openhook=fileinput.hook_encoded('utf-8'))]

    # JSON全体の文法チェック
    try:
        print('[JSON全体の文法性] ...', end='')
        json.loads('\n'.join(lines))
    except json.JSONDecodeError as e:
        print('エラーあり')
        print(e)
        exit(1)
    else:
        print('OK')

    # 先頭・末尾行のチェック
    print('[先頭行・末尾行] ...', end='')
    if lines[0] != '[':
        print('エラーあり')
        print('先頭行は "[" のみでなければなりません．')
        exit(1)
    if lines[-1] != ']':
        print('エラーあり')
        print('末尾行は "]" のみでなければなりません．')
        exit(1)
    print('OK')

    # 各レコードのチェック
    id_set = set()
    for i, line in enumerate(lines[1:-1]):    # type: int, str
        # 行末のカンマを取り除く
        line = line.rstrip(',')

        # 1行がJSONオブジェクトになっているかチェック
        try:
            obj = json.loads(
                line, object_pairs_hook=construct_dict)  # type: dict
            # 1行が1オブジェクトかどうか
            if type(obj) != dict:
                print('[line {0}] エラー，行が1つのオブジェクトになっていません．'.format(i+2))
                exit(1)
            # 識別子の存在チェック
            for id_key in id_fields[args.type[0]]:
                if id_key not in obj:
                    print('[line {0}] エラー，識別子 "{1}" が必要です．'.format(
                        i+2, id_key))
                    exit(1)
            # 出力値の存在チェック
            for out_key in output_fields[args.type[0]]:
                if out_key not in obj:
                    print('[line {0}] エラー，出力値 "{1}" が必要です．'.format(
                        i+2, out_key))
                    exit(1)
            # id重複チェック
            id_tuple = tuple([obj[k] for k in id_fields[args.type[0]]])
            if id_tuple in id_set:
                print('[line {0}] すでに出力済みの識別子を持つ行です．'.format(i+2))
                exit(1)
            id_set.add(id_tuple)

        except json.JSONDecodeError as e:
            print('[line {0}] 文法エラー，行が1オブジェクトになっていることを確認してください．'.format(i+2))
            print(e)
            exit(1)
        except AssertionError as e:
            print('[line {0}] エラー，{1}'.format(i+2, e))
            exit(1)
    print('チェック成功')


if __name__ == '__main__':
    main()
