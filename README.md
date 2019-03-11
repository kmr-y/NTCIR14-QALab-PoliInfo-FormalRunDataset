# Overview


[NTCIR14 QALab-PoliInfo](https://poliinfo.github.io) Formal Run は、2018年11月下旬から12月上旬にかけて開催されました。
このサイトでは、Formal Run で使用したデータセットを公開します。


## Three tasks:


1. Segmentation task
    - 目的：引用されている二次情報に対して、発言したとされる一次情報の該当範囲を提示する
    - 入力：質問と答弁の「発言の引用の対(つい)」とその発言が含まれる「議会会議録」
    - 出力：引用を理解するために読むべき発言の範囲 (「開始行」「終了行」)
2. Summarization task
    - 目的：議会の質問と答弁の構造を考慮して「発話者の意図を歪めない要約」を生成する
    - 入力：議会会議録に含まれる「発言」と要約の「制限字数」と「議会会議録」
    - 出力：発話者の意図が伝わる「要約」
3. Classification task
    - 目的：課題文と会議録に含まれる発言を比較し、関連、事実検証可能性、立場に分類することで、根拠のある意見をみつける
    - 入力：政策が記述された「課題文」と議会会議録中の「発言文（一文のみ）
    - 出力：３つのサブクラス「関連（有り、無し）」「事実検証(可能、不可能)」「立場(支持、不支持、どちらでもない)」を分類する


## Dataset
QA Lab-PoliInfoのデータセットは「地方議会会議録」「議会だより」を用いて作成しました。


## Sample for three tasks
* [FormalRun-sample-Segmentation.json](https://poliinfo.github.io/FormalRun-sample-Segmentation.json)
```json
[
    {
        "ID":"Segmentation-2018-JA-FormalSample-00001",
        "Prefecture":"東京都",
        "Date":"23-6-23",
        "Meeting":"平成23年_第２回定例会",
        "MainTopic":"東京の防災力向上は待ったなし<br>被災地復興には総合的取組を",
        "SubTopic":"都政運営",
        "QuestionSpeaker":"村上英子（自民党）",
        "QuestionSummary":"〔1〕国難のもとにおける東京の役割について所見を。〔2〕「10年後の東京」計画改定の視点は。〔3〕都民への責任果たし得る財政運営を。〔4〕被災地復興支援と首都東京の防災力向上に今後どう取り組むのか、所見を。",
        "AnswerSpeaker":"知事本局長",
        "AnswerSummary":"　〔2〕高度防災機能備えた都市へ取組強化等で安全・安心社会をつくり、節電意識徹底等で環境と経済が両立した都市実現等。",
        "QuestionStartingLine":763,
        "QuestionEndingLine":793,
        "AnswerStartingLine":1240,
        "AnswerEndingLine":1243    
    }
]
```


* [FormalRun-Sample-summarization.json](https://poliinfo.github.io/FormalRun-sample-Summarization.json)
```json
[
    {
        "ID":"Summarization-2018-JA-FormalSample-00001",
        "Prefecture":"東京都",
        "Date":"23-6-23",
        "Meeting":"平成23年_第２回定例会",
        "Speaker":"村上英子（自民党）",
        "MainTopic":"東京の防災力向上は待ったなし<br>被災地復興には総合的取組を",
        "SubTopic":"都政運営",
        "StartingLine":763,
        "EndingLine":793,
        "Summary":"〔1〕国難のもとにおける東京の役割について所見を。〔2〕「10年後の東京」計画改定の視点は。〔3〕都民への責任果たし得る財政運営を。〔4〕被災地復興支援と首都東京の防災力向上に今後どう取り組むのか、所見を。",
        "Length":"150字以内",
        "Source":"初めに、東日本大震災で亡くなられた方々のご冥福を心からお祈り申し上げ、被災された皆様にお見舞いを申し上げます。\\n改めて申し上げるまでもなく、政治の役割は、国民の生命、財産を守り、その生涯を安全に安心して暮らせるようにすることです。\\n未曾有の大震災にあって、我が都議会自由民主党は、一日も早い復旧、復興に全力を尽くしてまいります。\\n今回の大震災は、東北地方だけではなく、東日本全体に甚大な被害をもたらしました。\\nこうした事態にあって、菅政権の対応は、誤った政治主導により後手後手に回っており、極めて遺憾としかいいようがありません。\\n瓦れき撤去がおくれ、義援金も行き渡らない国とは対照的に、東京は、まさに獅子奮迅の働きをしています。\\nハイパーレスキュー隊の活躍で、日本は救われました。\\n警察官が大切なご遺体を遺族にお返しするために、捜索活動を今なお続けていることに深く敬意をあらわします。\\n都民から多大な義援物資、義援金も集まり、多くのボランティアが活躍しています。\\n避難を余儀なくされた被災者の方々を受け入れ、地域ぐるみで応援しています。\\nまさに国家にも匹敵する物的、人的な支援であり、これぞ首都であると思います。\\n知事に、国難のもとにおける東京の役割について、所見をお伺いいたします。\\n我々は、科学技術によって自然を従え、暑さ寒さをしのぎ、便利で快適な生活を当然と思ってきました。\\nしかし、電気がとまればすべてがとまって身動きができなくなった今回の事態に、かの物理学者、寺田寅彦が書いた「天災と国防」という論文の一節、文明が進めば進むほど、天然の暴威による災害が激烈の度を増すという一文が思い出されます。\\n大都市ほど、災害対策を、あらゆる角度から徹底してやらなければならないというのが、大きな教訓であると思います。\\n東京の弱点を徹底補強しなければ、首都として日本を牽引し続けることはできません。\\n先般、公表された都政運営の新たな戦略では、中長期的な都政運営の道筋を明らかにするため、「十年後の東京」計画を改定することが示されました。\\nどのような視点を持って改定に当たるのかお伺いいたします。\\n次に、財政運営について伺います。\\n今般の大震災は、都政を取り巻く環境に根本的な変化をもたらしました。\\nこのような中、今回、都は速やかに緊急対策を取りまとめ、震災からの本格的な復興に向けた一歩を歩み出しました。\\n財源探しに終始し、なかなか本格的な復興に向けた道筋を示すことができない国とは極めて対照的です。\\nしかしながら、首都東京を高度の防災機能を備えた都市としていくためには、中長期にわたる継続的な取り組みが必要であり、今後、これらの事業が本格化すれば、相当規模の財政支出が見込まれると考えます。\\n一方で、今回の震災による経済活動への影響が、歳入の根幹である都税収入の動向に今後どのように及ぶのか、注視していく必要があります。\\nまた、昨今の国における税制の抜本改革の検討の中では、都がこれまで繰り返し主張してきた法人事業税の暫定措置撤廃については、議論すらなされておらず、これに対しても都は強く主張していく必要があります。\\nこのように、都財政を取り巻く環境が大きく変化する中にあっても、今般取りまとめた緊急対策を着実に実行するとともに、今後も引き続き、都民に対する責任を果たし得る財政運営を図っていくべきと考えますが、所見を伺います。\\n次に、被災地の復興支援と首都東京の防災対策について伺います。\\n被災地の一刻も早い復旧、復興は、まさに国を挙げて取り組むべき課題であり、首都である東京は、全国からの支援の先頭に立ってさまざまな取り組みを行うことが求められています。\\n一方、都内でも、帰宅困難者の発生といった直接的な被害に加え、計画停電による生産活動の制約、雇用や景気の悪化など連鎖的な被害も生じています。\\n一千三百万都民の安全・安心の確保はもとより、日本全体への影響の大きさを考えると、東京の防災力向上は待ったなしです。\\nそこで、今回の大震災が突きつけた被災地の復興支援と首都東京の防災力向上という二つの課題に、今後どのように取り組むのか、知事の所見をお伺いいたします。\\n"
    }
]
```


* [FormalRun-sample-Classification.json](https://poliinfo.github.io/FormalRun-sample-Classification.json)
```json
[
	{
		"ID":"Classification-2018-JA-FormalSample-00001",
		"Topic":"築地市場を豊洲に移転するべきである",
		"Utterance":"豊洲は、新市場移転により千客万来施設ができるなど、今後、観光客の集客が大いに期待できるエリアであります。",
		"Relevance":1,"Fact-checkability":1,"Stance":1,"Class":1
	},
	{
		"ID":"Classification-2018-JA-FormalSample-00002",
		"Topic":"築地市場を豊洲に移転するべきである",
		"Utterance":"豊洲の新市場予定地では108箇所で液状化が発生し、築地市場の移転先としてふさわしくないことが重ねて証明されました。",
		"Relevance":1,"Fact-checkability":1,"Stance":2,"Class":2
	},
	{
		"ID":"Classification-2018-JA-FormalSample-00003",
		"Topic":"築地市場を豊洲に移転するべきである",
		"Utterance":"新銀行東京や築地市場の移転問題は非の立場です。",
		"Relevance":1,"Fact-checkability":0,"Stance":2,"Class":0
	},
	{	
		"ID":"Classification-2018-JA-FormalSample-00004",
		"Topic":"築地市場を豊洲に移転するべきである",
		"Utterance":"このような中、東京都はこの八月三十日に、豊洲の土壌汚染対策工事として、ゼネコン系の三つのＪＶと合計約五百四十二億円の契約を交わしています。",
		"Relevance":0,"Fact-checkability":1,"Stance":0,"Class":0
	},
	{
		"ID":"Classification-2018-JA-FormalSample-00005",
		"Topic":"築地市場を豊洲に移転するべきである",
		"Utterance":"豊洲新市場への移転を希望する事業者の不安を払拭すべく、移転資金や運転資金、移転後の新たな事業展開に必要な資金の手当てなど、経営支援策を講じてまいります。",
		"Relevance":1,"Fact-checkability":0,"Stance":0,"Class":0
	},
	{
		"ID":"Classification-2018-JA-FormalSample-00006",
		"Topic":"築地市場を豊洲に移転するべきである",
		"Utterance":"お正月五日の築地の初競りで史上最高となる一億五千五百四十万で落札された大間マグロはブランド化成功の代表例であります",
		"Relevance":0,"Fact-checkability":0,"Stance":0,"Class":0
	}
]
```



References

1. 木村泰知, 渋木英潔, 乙武北斗 内田ゆず, 高丸圭一, 阪本浩太郎, 石下円香, 三田村照子, 神門典子, NTCIR-14 QA Lab-PoliInfoの Formal Run Dataset の構築, 言語処理学会第25回年次大会(NLP2019),2019年3月.


