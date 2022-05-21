# qLearning
pythonによるQ学習

下記、箇所の行動を制限することができる。

制限された行動の中で、Q学習を行い迷路を解決する。
```python
ACTIO= (
        "FORWARD_MARCH",    #前に進め
        "BACKWARD_MARCH",   #後ろに進め
        "RIGHT_FACE",       #右向け右
        "LEFT_FACE",        #左向け左
        )
```

ALL.txtは、すべて行動ができる場合の結果

FORWARD_LEFT.txtは、「前に進め」と「左向け左」しかできない結果
