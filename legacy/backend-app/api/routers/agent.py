from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.agent import LessonGenerateRequest, LessonGenerateResponse
from app.schemas.common import ApiResponse

router = APIRouter(prefix="/agent", tags=["AI Agent"])

MOMENTUM_LESSON_MOCK = {
    "title": "动量守恒实验的沉浸式课堂设计",
    "markdown_content": """# 动量守恒实验的沉浸式课堂设计

## 一、教学目标

### 1.1 知识与技能
- 理解动量守恒定律的物理含义及适用条件
- 掌握动量守恒定律在碰撞、爆炸等典型场景中的定量计算
- 能够设计并分析验证动量守恒的实验方案

### 1.2 过程与方法
- 通过气垫导轨实验，经历"提出假设 → 设计实验 → 采集数据 → 验证定律"的完整探究过程
- 运用数字化实验传感器（力传感器、光电门），培养数据处理与分析能力

### 1.3 情感态度与价值观
- 感受物理定律的简洁美与普适性
- 通过"天宫课堂"太空实验视频，激发对前沿科技的兴趣
- 培养严谨求实的科学态度与团队协作精神

---

## 二、教学重难点

| 类型 | 内容 |
|------|------|
| **重点** | 动量守恒定律的理解与适用条件；实验方案的设计与数据分析 |
| **难点** | 区分"系统内力"与"外力"；处理实验中的误差来源 |

---

## 三、教学流程设计（45分钟）

### 环节一：情境导入（5分钟）
**🎥 视频引入**
播放"天宫课堂"中太空碰撞实验片段，引导学生思考：
- 太空中两个小球碰撞前后，总动量是否变化？
- 如果没有外力作用，系统的总动量会如何？

### 环节二：概念建构（10分钟）
1. **回顾动量**：$\\vec{p} = m\\vec{v}$
2. **动量定理**：$\\vec{F}_{合}\\Delta t = \\Delta\\vec{p}$
3. **推导动量守恒**：
   - 对于系统 $A+B$，内力满足 $\\vec{F}_{AB} = -\\vec{F}_{BA}$
   - 当系统合外力为零时：$\\Delta\\vec{p}_{总} = 0$
   - 即：$m_1\\vec{v}_1 + m_2\\vec{v}_2 = m_1\\vec{v}_1' + m_2\\vec{v}_2'$

### 环节三：实验探究（20分钟）
**气垫导轨验证实验**

| 步骤 | 操作 | 观测目标 |
|------|------|----------|
| 1 | 调节导轨水平 | 确保滑块不受额外外力 |
| 2 | 让滑块A以速度 $v_1$ 撞向静止滑块B | 完全非弹性碰撞 |
| 3 | 记录光电门数据 | 测量碰撞前后速度 |
| 4 | 计算 $m_1v_1$ 与 $(m_1+m_2)v'$ | 验证等量关系 |

**🚨 误差分析引导**：
- 导轨是否真正水平？
- 空气阻力是否可以忽略？
- 光电门计时精度的影响？

### 环节四：迁移应用（8分钟）
**案例讨论**：
1. 冰壶运动员掷出冰壶后为何向后滑动？（反冲）
2. 子弹打入木块的过程，动量是否守恒？
3. $$\\frac{1}{2}m_1v_1^2$$ 碰撞前后的动能变化说明了什么？

### 环节五：课堂小结（2分钟）
学生自主总结：
- 动量守恒定律的内容与条件
- 实验中的关键操作要点
- 生活中的动量守恒现象

---

## 四、课后延伸

### 分层作业
- **基础题**：教材课后练习第3-5题
- **提升题**：设计一个实验，验证斜碰中的动量守恒
- **拓展阅读**：火箭推进原理中的动量守恒

### 下节预告
动量守恒与能量守恒的综合应用——碰撞分类专题

---

> 📌 本教案由织课 AI 智能生成，教师可根据实际学情灵活调整难度与节奏。""",
    "content_format": "markdown",
}


@router.post("/generate/lesson", response_model=ApiResponse[LessonGenerateResponse])
def generate_lesson(body: LessonGenerateRequest, db: Session = Depends(get_db)):
    return ApiResponse(
        code=200,
        msg="success",
        data=LessonGenerateResponse(
            title=MOMENTUM_LESSON_MOCK["title"],
            markdown_content=MOMENTUM_LESSON_MOCK["markdown_content"],
            content_format=MOMENTUM_LESSON_MOCK["content_format"],
        ),
    )
