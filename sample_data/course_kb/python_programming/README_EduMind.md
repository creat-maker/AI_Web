# EduMind Python 程序设计课程知识库

本目录用于软件杯 A3 赛题的 RAG 示例课程资料集，课程建议命名为：

**Python 程序设计：从基础语法到爬虫实践**

## 课程定位

该知识库面向高校计算机、软件工程、人工智能导论类课程，覆盖：

- Python 基础语法：字符串、列表、字典、分支、循环
- 程序结构：函数、模块、高阶函数、面向对象
- 工程实践：文件读写、异常处理、日志工具
- 网络爬虫：HTTP 请求、网页解析、数据存储、反爬与合规

这条主线适合 EduMind 演示：

画像构建 -> RAG 课程问答 -> 个性化资源生成 -> 代码案例 -> 测验评价 -> 学习报告。

## 当前资料来源

| 目录 | 说明 | 本地授权状态 |
| --- | --- | --- |
| `edumind_curated` | EduMind 为比赛演示整理的课程大纲、短讲义、题库和实践任务 | EduMind original |
| `python-tutorial-master` | Python 基础、高级特性、Flask、爬虫、工具脚本等教程 | 已包含 `LICENSE`，Apache-2.0 |
| `Python-100-Days-master` | Python 100 天学习路径，基础语法、文件异常、爬虫、工程化等资料 | 已获团队授权确认；提交前仍需在开源/授权说明中标注来源与授权依据 |

## 默认导入范围

为了降低提交风险，导入脚本默认导入 `edumind_curated` 原创整理资料和 `python-tutorial-master` 中 license 明确的精选资料。

`edumind_curated` 默认导入：

- `00_course_syllabus.md`
- `01_data_structures.md`
- `02_files_exceptions.md`
- `03_web_crawler_practice.md`
- `04_question_bank.md`

`python-tutorial-master` 默认导入：

- `README.md`
- `01_base/README.md`
- `01_base/01_字符串类型_str.ipynb`
- `01_base/02_列表类型_list.ipynb`
- `01_base/04_字典类型_dict.ipynb`
- `01_base/06_条件判断_if.ipynb`
- `01_base/08_循环结构_loop.ipynb`
- `01_base/09_函数和模块.ipynb`
- `01_base/10_文件和异常.ipynb`
- `02_advanced/03_高阶函数.ipynb`
- `02_advanced/07_面向对象编程.ipynb`
- `05_spider/README.md`
- `05_spider/01_爬虫介绍.ipynb`
- `05_spider/02_网页解析和存储.ipynb`
- `06_tool/logger.py`

当前已确认 `Python-100-Days-master` 获授权，可使用参数额外导入更完整的 Markdown 教材资料。

## 导入命令

在项目根目录运行：

```bash
python scripts/import_python_programming_kb.py
```

导入 license 明确资料 + Python-100-Days 精选资料：

```bash
python scripts/import_python_programming_kb.py --include-python-100-days
```

脚本会自动：

1. 创建或复用课程 `Python 程序设计：从基础语法到爬虫实践`
2. 解析 Markdown、Jupyter Notebook、Python 代码文件
3. 按章节/段落进行 RAG 切片
4. 写入 `course_documents`
5. 构建 Chroma 向量索引；若 Chroma 不可用，则写入 JSON fallback 索引

## 推荐演示问题

- Python 列表和字典分别适合什么场景？
- Python 函数和模块有什么作用？
- with open 为什么比手动 close 更安全？
- Python 爬虫发送 HTTP 请求的基本步骤是什么？
- 爬虫请求失败时应该先检查什么？
- BeautifulSoup 和正则表达式解析网页有什么区别？

## 提交说明

比赛提交文档中应在“开源项目与协议”章节标注：

- `python-tutorial`，来源：`python-tutorial-master`，协议：Apache License 2.0。
- `Python-100-Days`，来源：`Python-100-Days-master`，已获团队授权确认；提交包和项目文档中需补充授权依据、来源链接或授权证明说明。
