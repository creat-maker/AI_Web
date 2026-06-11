# Python 文件读写与异常处理

## 文件读写的基本流程

文件读写通常包含三个步骤：打开文件、读取或写入内容、关闭文件。直接使用 `open()` 后手动 `close()` 是可行的，但如果中间发生异常，文件可能无法被正常关闭。

```python
file = open("data.txt", "r", encoding="utf-8")
content = file.read()
file.close()
```

## with open 为什么更安全

`with open` 会创建上下文管理器。代码块执行结束后，无论是否发生异常，Python 都会自动调用文件对象的关闭逻辑，因此比手动 `close()` 更安全、更简洁。

```python
with open("data.txt", "r", encoding="utf-8") as file:
    content = file.read()
```

在项目实践中，读取课程资料、保存爬虫结果、写入学习日志时，都建议使用 `with open`。

## 常见打开模式

| 模式 | 含义 | 场景 |
| --- | --- | --- |
| `r` | 只读 | 读取已有文本 |
| `w` | 写入，会覆盖原文件 | 生成新结果 |
| `a` | 追加写入 | 写日志 |
| `rb` | 二进制读取 | 图片、PDF |
| `wb` | 二进制写入 | 保存图片 |

## 异常处理

文件读写可能出现文件不存在、编码错误、权限不足等问题。可以使用 `try-except` 捕获异常。

```python
try:
    with open("score.txt", "r", encoding="utf-8") as file:
        data = file.read()
except FileNotFoundError:
    print("文件不存在，请检查路径")
except UnicodeDecodeError:
    print("文件编码不正确")
```

## 学习建议

基础薄弱学生应先掌握文本文件读取，再学习 CSV、JSON 等结构化数据。调试时要先检查文件路径、编码和打开模式。

## 练习题

1. 读取一个成绩文件，统计平均分。
2. 把学生画像字典保存为 JSON 文件。
3. 故意读取不存在的文件，并用异常处理给出友好提示。
