# 第 6 章 文件读写

本章覆盖 `with open`、文本读写、编码、CSV 和异常兜底。

```python
with open("scores.txt", "r", encoding="utf-8") as f:
    for line in f:
        print(line.strip())
```
