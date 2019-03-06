# （2019/01/23更新）結果公開と評価

## 評価スクリプトの使用方法
* 以下のように評価スクリプトを適用する．

    ```
    python3 poliinfo_eval_formal_segmentation.py -g FormalTestGS-Segmentation-FormalRun.json -o output_directory -i input_file1 [input_file2 ...]
    ```

    * ```-o```オプションで指定したディレクトリにはインスタンスごとの結果が出力されます．
    * 標準出力には```-i```オプションで指定したすべての入力データの総合評価結果が出力されます．

Formal Runの提出データと評価結果を本リポジトリで公開しています．
各ディレクトリ，ファイルの内容は以下の通りです．

* ```evals```ディレクトリ
    * ```Result-FormalTest-Segmentation-FormalRun_[GROUP_ID]-[PRIORITY].xlsx```
        * ```[GROUP_ID]```の```[PRIORITY]```提出における各インスタンスの正誤結果です．
        * ```Precision```列: [一致] / [解答範囲が表す個数]（QuestionとAnswerを合わせたもの）
        * ```Recall```列: [一致] / [正解範囲が表す個数]（QuestionとAnswerを合わせたもの）
        * ```Q-解答```列: 提出結果のQuestionの出力値
        * ```Q-正解```列: Questionの正解値
        * ```Q-一致```列: Questionの解答が示す範囲が正解値とどれだけ一致しているか
        * ```Q-Precision```列: [一致] / [解答範囲が表す個数]（Question）
        * ```Q-Recall```列: [一致] / [正解範囲が表す個数]（Question）
        * ```A-*```各列: Answerにおける情報（Questionと同項目）
* ```submits```ディレクトリ
    * 本タスクにて提出されたすべてのAnswerSheetデータを配置しています．
* ```eval-Segmentation-2018-JA-Formal.xlsx```
    * 全提出データを対象とした評価結果一覧です．
    * ```lines```列: 全正解範囲が表す個数の総和
    * ```output```列: 全解答範囲が表す個数の総和
    * ```match```列: ```一致```の総和
    * ```Precision```列: [match] / [output]
    * ```Recall```列: [match] / [lines]

# Formal Run提出データの書式チェッカースクリプトについて

Formal Run提出データ（Answer Sheet）の書式をチェックするPythonスクリプトです．
結果を提出する際は，本スクリプトによるチェックをパスしたファイルを提出してください．

## 動作環境

* Python 3.5以上
    * Windows, macOS, Linux環境で動作確認済み

## 使用方法

```bash
python3 poliinfo_check_format2.py [-h] -t {seg,sum,cls} json_file
```

* 必須引数:
    * ```json_file```: 対象JSONファイル（指定しない場合は標準入力から読み込みます）
    * ```-t {seg,sum,cls}, --type {seg,sum,cls}```: 対象ファイルの種別を指定し
        * (```seg```:Segmentation, ```sum```:Summarization, ```cls```:Classification)
* オプション引数:
    * ```-h, --help```: ヘルプ表示
  
| 実行結果 | 意味 |
|:--------|:----|
| チェックOK | 書式チェックをすべてパスしたことを表します． |
| [JSON全体の文法性] ...エラーあり | ファイルがJSONの書式を満たしていないことを表します．エラーの内容と箇所も併せて表示されます． |
| 先頭行は "[" のみでなければなりません． | 本提出データの先頭行は ```[``` のみとしてください． |
| 末尾行は "]" のみでなければなりません． | 本提出データの末尾行は ```]``` のみとしてください． |
| [line *n*] エラー，行が1つのオブジェクトになっていません． | （ファイルの*n*行目について）1行につき1つのオブジェクト表記としてください． |
| [line *n*] エラー，出力値 "xxx" が必要です． | （ファイルの*n*行目について）出力値として必須である ```xxx``` 項目が欠如しています． |
| [line *n*] エラー，識別子 "ID" が必要です． | （ファイルの*n*行目について）識別子として必須である ```ID``` 項目が欠如しています． |
| [line *n*] すでに出力済みの識別子を持つ行です． | （ファイルの*n*行目について）このIDのインスタンスは以前の行で出力済みです． |
| [line *n*] エラー，同名のフィールドが複数存在します．． | （ファイルの*n*行目について）同名の項目が2つ以上存在してはいけません． |