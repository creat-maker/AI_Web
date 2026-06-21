from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict


router = APIRouter(prefix="/ai-tutor", tags=["ai-tutor"])


class TutorAskPayload(BaseModel):
    model_config = ConfigDict(extra="allow")

    question: str = "为什么我的 while 循环会死循环？"
    mode: str = "基础补弱"
    studentId: str | None = "student-li-ming"
    courseName: str | None = "Python 程序设计"


REFERENCE_SOURCE = "Python 程序设计课程知识库 / 循环结构章节"
SCRIPT_READY_MESSAGE = "讲解脚本已生成，可用于后续语音播报或数字人服务。"


def _topic_payload(question: str) -> dict[str, str]:
    normalized = question.lower()
    if ("for" in normalized and "while" in normalized) or "怎么选择" in question:
        return {
            "diagnosis": "你主要需要根据循环次数是否明确来选择循环结构。",
            "explanation": "次数明确、遍历序列时优先用 for；需要满足某个条件才结束、次数不固定时优先用 while。",
            "wrongExample": "while i < len(nums):\n    print(nums[i])\n    i += 1\n# 只是遍历列表时写法偏绕，容易漏掉 i 的初始化或更新",
            "correctExample": "for item in nums:\n    print(item)\n\nwhile password != 'ok':\n    password = input('请输入密码：')",
            "commonMistakes": "把所有循环都写成 while，导致忘记初始化或更新变量；或在次数不确定的输入校验场景强行使用 for。",
            "practice": "把 2 个列表遍历题改写成 for，再把 2 个输入校验题改写成 while。",
            "nextPath": "先完成 for / while 选择题，再进入 while 条件更新专项练习。",
            "script": "先问学生循环次数是否提前知道，再用列表遍历和密码输入两个场景对比 for 与 while 的选择。"
        }
    if "break" in question or "continue" in question:
        return {
            "diagnosis": "你主要卡在循环控制语句的作用范围：break 结束当前循环，continue 跳过本轮剩余语句。",
            "explanation": "判断输出结果时，先确认语句执行到 break 还是 continue，再看是否进入下一轮循环。",
            "wrongExample": "for i in range(5):\n    if i == 2:\n        continue\n    print('结束循环')\n# 这里 continue 不会结束整个循环",
            "correctExample": "for i in range(5):\n    if i == 2:\n        break\n    print(i)\n# 如果要结束循环，应使用 break",
            "commonMistakes": "把 continue 当成结束整个循环，或把 break 放在错误的条件分支中。",
            "practice": "完成 6 道输出结果判断题，并解释每一轮是否继续执行。",
            "nextPath": "先做 break / continue 对比卡，再进入循环嵌套综合练习。",
            "script": "先说明 break 是结束循环，continue 是跳过本轮，再逐行追踪 i 等于 2 时程序执行到哪里。"
        }
    if "嵌套" in question:
        return {
            "diagnosis": "你主要需要跟踪内外层循环变量的变化顺序。",
            "explanation": "外层循环每执行一次，内层循环通常会完整执行一轮。建议把外层变量和内层变量分列记录。",
            "wrongExample": "for i in range(3):\n    for i in range(2):\n        print(i)\n# 内外层变量同名，会让追踪过程混乱",
            "correctExample": "for i in range(3):\n    for j in range(2):\n        print(i, j)",
            "commonMistakes": "内外层变量同名，或只记录输出结果，不记录每轮变量变化。",
            "practice": "补全九九乘法表，并写出前 3 轮 i、j 的变化。",
            "nextPath": "先画变量变化表，再完成循环嵌套代码补全。",
            "script": "先把外层循环理解成行，内层循环理解成每一行里的列，再用 i、j 表格记录前三轮变化。"
        }
    return {
        "diagnosis": "while 死循环通常来自循环条件一直为 True，或循环变量没有在循环体内更新。",
        "explanation": "按“初始值、循环条件、变量更新”三步检查，确认每一轮循环都会让条件逐步接近结束。",
        "wrongExample": "i = 0\nwhile i < 5:\n    print(i)\n# 缺少 i += 1，条件会一直成立",
        "correctExample": "i = 0\nwhile i < 5:\n    print(i)\n    i += 1",
        "commonMistakes": "忘记更新变量、条件方向写反、continue 跳过了变量更新语句。",
        "practice": "完成 3 道 while 循环补全题，要求写出前三轮变量变化。",
        "nextPath": "进入“诊断补弱 -> 核心概念学习 -> 案例实操”的前三个节点。",
        "script": "先定位循环条件为什么一直成立，再展示缺少变量更新的错误代码，最后用正确代码说明每一轮 i 如何变化。"
    }


@router.post("/ask")
def ask(payload: TutorAskPayload) -> dict[str, Any]:
    topic = _topic_payload(payload.question)
    citation = REFERENCE_SOURCE
    script = f"{SCRIPT_READY_MESSAGE}讲解顺序：{topic['script']}"
    cards = [
        {"title": "问题诊断", "content": topic["diagnosis"]},
        {"title": "简明解释", "content": topic["explanation"]},
        {"title": "错误示例", "content": topic["wrongExample"]},
        {"title": "正确示例", "content": topic["correctExample"]},
        {"title": "常见错误", "content": topic["commonMistakes"]},
        {"title": "推荐练习", "content": topic["practice"]},
        {"title": "下一步路径", "content": topic["nextPath"]},
        {"title": "引用依据", "content": citation},
        {"title": "依据风险", "content": "低"},
        {"title": "讲解脚本", "content": script},
    ]
    answer_text = "\n".join(f"{card['title']}：{card['content']}" for card in cards)
    return {
        "status": "智能回答",
        "mode": payload.mode,
        "studentName": "李明",
        "courseName": payload.courseName,
        "question": payload.question,
        "answer": answer_text,
        "content": answer_text,
        "cards": cards,
        "structuredAnswer": {
            "diagnosis": topic["diagnosis"],
            "explanation": topic["explanation"],
            "wrongExample": topic["wrongExample"],
            "correctExample": topic["correctExample"],
            "commonMistakes": topic["commonMistakes"],
            "practice": topic["practice"],
            "nextPath": topic["nextPath"],
            "citation": citation,
            "evidenceRisk": "低",
            "script": script,
        },
        "reviewStatus": "通过",
        "citation": citation,
        "citations": [{"sourceFile": "python_programming.json", "chapter": "循环结构", "section": "while 循环", "snippet": citation}],
        "confidence": 0.86,
        "lowEvidenceRisk": "低",
        "recommendedExercises": [topic["practice"]],
        "nextLearningPath": topic["nextPath"],
        "digitalHumanScript": script,
    }


@router.post("/digital-human-script")
def digital_human_script(payload: TutorAskPayload) -> dict[str, Any]:
    topic = _topic_payload(payload.question)
    sections = [
        {"title": "开场白", "content": f"李明，我们围绕 {payload.courseName or 'Python 程序设计'} 的循环结构，把这道问题拆成可以逐步检查的步骤。"},
        {"title": "知识点解释", "content": topic["explanation"]},
        {"title": "错误代码讲解", "content": topic["wrongExample"]},
        {"title": "正确代码讲解", "content": topic["correctExample"]},
        {"title": "常见错误提醒", "content": topic["commonMistakes"]},
        {"title": "练习建议", "content": topic["practice"]},
        {"title": "总结", "content": f"{topic['diagnosis']}下一步建议：{topic['nextPath']}"},
    ]
    return {
        "status": "已生成",
        "avatar": "AI 学伴讲解脚本",
        "message": SCRIPT_READY_MESSAGE,
        "sections": sections,
        "script": f"{SCRIPT_READY_MESSAGE}\n" + "\n".join(f"{item['title']}：{item['content']}" for item in sections),
        "nextStep": topic["nextPath"],
        "lowEvidenceRisk": "低",
    }
