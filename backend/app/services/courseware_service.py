from __future__ import annotations

from dataclasses import dataclass


DEFAULT_COURSE = "Python 程序设计"
DEFAULT_CHAPTER = "循环结构"
DEFAULT_STUDENT = "李明"
DEFAULT_WEAK_POINTS = "while 循环和循环嵌套需要加强"


@dataclass(frozen=True)
class CoursewareRequest:
    course: str = DEFAULT_COURSE
    chapter: str = DEFAULT_CHAPTER
    student: str = DEFAULT_STUDENT
    weak_points: str = DEFAULT_WEAK_POINTS


def build_courseware_outline(request: CoursewareRequest) -> dict:
    course = request.course.strip() or DEFAULT_COURSE
    chapter = request.chapter.strip() or DEFAULT_CHAPTER
    student = request.student.strip() or DEFAULT_STUDENT
    weak_points = request.weak_points.strip() or DEFAULT_WEAK_POINTS

    sections = [
        {
            "title": "课程导入",
            "objective": "用计数和重复执行场景引出循环结构的作用。",
            "bullets": [
                "从重复输出和累计求和问题切入",
                f"说明本节课面向 {student} 的补弱重点",
                "建立“条件、变量、循环体”的观察框架",
            ],
        },
        {
            "title": "for 循环",
            "objective": "掌握已知次数或遍历序列时的循环写法。",
            "bullets": [
                "range 的起点、终点和步长",
                "遍历字符串、列表和数值区间",
                "与 while 循环的适用场景对比",
            ],
        },
        {
            "title": "while 循环",
            "objective": "重点强化条件更新和终止条件判断。",
            "bullets": [
                "初始值、循环条件、变量更新三步检查",
                "用变量变化表分析前三轮执行过程",
                "定位死循环和条件方向写反的问题",
            ],
        },
        {
            "title": "break / continue",
            "objective": "区分结束循环和跳过本轮的控制逻辑。",
            "bullets": [
                "break 结束当前循环",
                "continue 跳过本轮剩余语句",
                "结合输出结果题逐行追踪执行路径",
            ],
        },
        {
            "title": "循环嵌套",
            "objective": "理解内外层变量变化和执行顺序。",
            "bullets": [
                "外层控制行，内层控制列",
                "避免内外层变量同名",
                "用九九乘法表观察嵌套结构",
            ],
        },
        {
            "title": "常见错误",
            "objective": "把李明的薄弱点转化为可检查清单。",
            "bullets": [
                "忘记更新 while 循环变量",
                "continue 跳过变量更新语句",
                "循环嵌套中混用内外层变量",
            ],
        },
        {
            "title": "课堂练习",
            "objective": "通过即时练习验证循环结构掌握情况。",
            "bullets": [
                "补全 while 条件更新代码",
                "判断 break / continue 输出结果",
                "追踪嵌套循环前三轮变量变化",
            ],
        },
        {
            "title": "课后任务",
            "objective": "将循环结构迁移到小型程序任务。",
            "bullets": [
                "完成 3 道循环补全题",
                "改写 2 个 for / while 选择场景",
                "提交一段带变量变化说明的嵌套循环代码",
            ],
        },
    ]

    return {
        "course": course,
        "chapter": chapter,
        "student": student,
        "weakPoints": weak_points,
        "title": f"{course}《{chapter}》AI 课件大纲",
        "outline": sections,
        "statusMessage": "已生成课件大纲",
        "libraryMessage": "已加入教学资源库",
        "exportMessage": "可用于后续导出 PPT",
        "capabilityNote": "当前提供课件大纲与资源库入库结果，PPTX 导出接口已预留。",
    }
