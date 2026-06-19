from __future__ import annotations

from fastapi import APIRouter


router = APIRouter(prefix="/decision-center", tags=["decision-center"])


@router.get("/overview")
def overview():
    return {
        "title": "EduMind 教学智能决策中心",
        "metrics": [
            {"label": "AI 生成资源数", "value": 286, "unit": "份"},
            {"label": "学生画像数量", "value": 128, "unit": "份"},
            {"label": "学习预警人数", "value": 12, "unit": "人"},
            {"label": "学习路径完成率", "value": 76.8, "unit": "%"},
            {"label": "内容审核通过率", "value": 91.2, "unit": "%"},
            {"label": "AI 学伴使用次数", "value": 18620, "unit": "次"},
        ],
        "heatmap": [
            {"knowledgePoint": "for 循环", "mastery": 72},
            {"knowledgePoint": "while 循环", "mastery": 48},
            {"knowledgePoint": "break / continue", "mastery": 55},
            {"knowledgePoint": "循环嵌套", "mastery": 43},
        ],
        "agentStatus": [
            {"name": "画像构建 Agent", "status": "运行正常"},
            {"name": "知识检索 Agent", "status": "运行正常"},
            {"name": "资源生成 Agent", "status": "运行正常"},
            {"name": "内容安全与防幻觉审核 Agent", "status": "待人工复核 3 项"},
        ],
        "miniprogramActive": {"todayUsers": 86, "weeklyRetention": "68%"},
        "teacherEfficiency": {"savedHours": 42, "autoReports": 56, "recommendedInterventions": 18},
        "mode": "mock-fallback",
    }
