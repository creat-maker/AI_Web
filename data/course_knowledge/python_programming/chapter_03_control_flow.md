# 第 3 章 控制流：循环结构

本章是 EduMind 主演示章节，围绕李明的 Python 循环结构专项补弱展开。

## 学习目标

- 能用 `if / elif / else` 表达条件分支。
- 能区分 `for` 循环和 `while` 循环。
- 能正确使用 `range()` 控制循环次数。
- 能解释 `break` 和 `continue` 对循环流程的影响。
- 能读懂和编写简单循环嵌套代码。
- 能识别死循环、少循环一次、多循环一次等常见错误。

## if 条件判断

条件判断用于根据布尔表达式选择不同分支。

```python
score = 76
if score >= 90:
    level = "优秀"
elif score >= 60:
    level = "合格"
else:
    level = "待补强"
print(level)
```

常见错误：

- 把 `=` 写成比较条件。
- 忘记冒号。
- 嵌套层级过深，导致逻辑难以检查。

## for 循环

`for` 适合遍历序列或明确次数的重复任务。

```python
for i in range(5):
    print(i)
```

`range(5)` 生成 `0, 1, 2, 3, 4`。如果需要从 1 到 5：

```python
for i in range(1, 6):
    print(i)
```

## while 循环

`while` 适合未知次数、由条件控制的重复任务。关键是循环变量必须推进到终止条件。

```python
i = 0
while i < 5:
    print(i)
    i += 1
```

死循环常见原因：

- 忘记 `i += 1`。
- 条件写成永远成立。
- 在 `continue` 前跳过了变量更新。

## range 函数

`range(start, stop, step)` 生成左闭右开的整数序列。

```python
for i in range(2, 11, 2):
    print(i)
```

输出 2、4、6、8、10。

## break

`break` 立即结束当前循环，常用于找到目标后退出。

```python
for n in range(1, 10):
    if n == 5:
        break
    print(n)
```

## continue

`continue` 跳过本轮剩余代码，进入下一轮循环。

```python
for n in range(1, 6):
    if n == 3:
        continue
    print(n)
```

注意：在 `while` 中使用 `continue` 时，变量更新必须放在 `continue` 之前或确保不会被跳过。

## 循环嵌套

循环嵌套用于处理表格、矩阵、组合枚举等场景。

```python
for row in range(1, 4):
    for col in range(1, 4):
        print(row, col)
```

九九乘法表：

```python
for i in range(1, 10):
    for j in range(1, i + 1):
        print(f"{j}*{i}={i*j}", end="\t")
    print()
```

## 代码案例：猜数字

```python
target = 7
count = 0

while True:
    guess = int(input("请输入 1-10 的数字："))
    count += 1
    if guess == target:
        print("猜对了，共尝试", count, "次")
        break
    if guess < target:
        print("太小了")
    else:
        print("太大了")
```

## 常见错误清单

- `while` 循环变量没有更新，导致死循环。
- `range(1, 5)` 误以为包含 5。
- `break` 只能结束当前所在的一层循环。
- `continue` 导致后续更新语句被跳过。
- 内外层循环变量混用。
- 嵌套循环没有先画行列关系，导致输出格式错误。

## 练习题

1. 用 `for` 输出 1 到 100 中所有偶数。
2. 用 `while` 输出 0 到 4，并说明每一轮变量如何变化。
3. 修改一个会死循环的 `while` 程序。
4. 使用 `break` 实现输入 `q` 时退出。
5. 使用 `continue` 跳过列表中的负数。
6. 编写九九乘法表。
7. 统计列表中大于 60 的成绩数量。
8. 用嵌套循环输出 4 行星号三角形。

## RAG 引用元数据

- 引用来源：data/course_knowledge/python_programming/chapter_03_control_flow.md
- 置信度建议：命中 while / for / break / continue / 循环嵌套时为高
- 低依据风险：如果问题超出循环结构范围，需要提示教师复核
- 推荐下一步：进入“诊断补弱 -> 核心概念学习 -> 案例实操”路径
