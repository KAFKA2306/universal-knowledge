# 参考研究と実装の関係

この試作は次の2研究を参考に設計した独立したコードです。論文の実装や評価結果を再現したものではありません。

1. Costa, D. P. ほか（2026年10月29日公開）。*A training-free, domain-extensible LLM-based approach for automated extraction of standardized preparation procedures*（Nature Communications）。[論文の原文](https://doi.org/10.1038/s41467-026-78605-7)、[関連実装](https://github.com/DigicatPT-IST/xlmexlab)。論文の対象は研究室での調製手順です。この試作は操作定義を分野ごとに差し替える考え方を参考にしていますが、コードは独立して作成しました。
2. Yang, H. / Buehler, M. J.（2026年10月27日提出）。*Prospector: learning a compact graph traversal policy for scientific reasoning*。[arXiv:2610.37121](https://arxiv.org/abs/2610.37121)。論文は探索方針を学習したモデルを扱っています。この試作はグラフ形式で抽出結果を保存するだけで、Prospectorの学習済み探索方針は実装していません。

UIの正本は [KAFKA2306/design](https://github.com/KAFKA2306/design)、共通プロンプトの正本は [KAFKA2306/prompt-vault](https://github.com/KAFKA2306/prompt-vault) です。現在の試作はこれらの成果物を取り込んでいません。

論文に掲載された性能値は、同じ評価条件で本プロジェクトの結果を測定するまで、ここでの性能値として使用しません。
