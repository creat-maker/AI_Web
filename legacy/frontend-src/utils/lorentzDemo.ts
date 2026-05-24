import type { GeneratedContentEntry } from '../types';

export interface LorentzDemoContext {
  projectName?: string | null;
  fileNames?: string[];
  attachmentIds?: number[];
  sourceFiles?: string[];
  userRequirement?: string;
}

export const LORENTZ_DEMO_KEYWORD = '洛伦兹力';

export const LORENTZ_DEMO_STAGE_MESSAGES = [
  '正在构建 3D 物理场景...',
  '正在同步学情分析...',
  '正在生成交互动画引擎...',
] as const;

export const LORENTZ_DEMO_LESSON_PLAN_MARKDOWN = `# 🧲 《洛伦兹力与带电粒子在磁场中的运动》标准示范教案

> **适用年级**：高二物理（选修） | **预计课时**：45分钟 | **学情分析**：学生已掌握安培力与磁感应强度概念，具备基础的空间几何想象能力。

---

## 一、 核心教学目标

### 1.1 物理观念 (Physical Concept)
- **洛伦兹力概念**：深刻理解运动电荷在磁场中所受到的力，建立"宏观安培力是微观洛伦兹力宏观表现"的跨尺度认知。
- **方向判定**：熟练掌握**左手定则**判断受力方向（四指指向正电荷运动方向，磁感线穿过手心，大拇指指向受力方向）。
- **运动机制**：理解带电粒子在匀强磁场中，仅受洛伦兹力时做**匀速圆周运动**的物理机制。

### 1.2 科学思维 (Scientific Thinking)
- 能够通过逻辑推理，将宏观导线受力公式推导至微观单个电荷受力公式。
- 构建三维正交坐标系，解决速度方向与磁场方向呈任意夹角时的螺旋线运动模型。

---

## 二、 教学重难点剖析

| 维度 | 核心内容 | 突破策略预案 |
| :--- | :--- | :--- |
| **重点** | 洛伦兹力公式 $F = qvB$ 及左手定则的应用 | 引入右侧【拟真演示】沙盒，让学生拖拽参数观察粒子偏转 |
| **难点** | 空间立体思维，动态圆周运动的半径与周期推导 | 结合 3D 动画拆解受力分析，使用对比法区分正负电荷 |
| **易错点** | 忽略洛伦兹力**始终不做功**的物理特性 | 从动能定理 $W = \\Delta E_k$ 角度切入进行数学证明 |

---

## 三、 核心公式推导与推演

### 3.1 基础公式定型
当带电粒子的运动方向与磁场方向垂直（$v \\perp B$）时，洛伦兹力达到最大值：
$$F = qvB$$
*(注：若 $v$ 与 $B$ 夹角为 $\\theta$，则一般式为 $F = qvB\\sin\\theta$)*

### 3.2 匀速圆周运动两大核心方程
洛伦兹力提供全部向心力，根据牛顿第二定律，推导轨道半径 $r$：
$$qvB = m\\frac{v^2}{r} \\implies \\boxed{r = \\frac{mv}{qB}}$$

推导粒子运动周期 $T$（极度重要：周期与速度、半径均无关！）：
$$T = \\frac{2\\pi r}{v} = \\frac{2\\pi}{v} \\left(\\frac{mv}{qB}\\right) \\implies \\boxed{T = \\frac{2\\pi m}{qB}}$$

---

## 四、 教学过程设计 (45 mins)

### 环节一：情境导入 (5 mins)
- **播放素材**：极光 (Aurora) 现象的真实录像。
- **提出疑问**：太阳风中的高能粒子为何在地球两极聚集并发光？引导出地球磁场对运动电荷的作用。

### 环节二：新课讲授与公式推导 (15 mins)
- **知识迁移**：从安培力 $F_{amp} = BIL$ 出发。设导线中单位体积内自由电荷数为 $n$，截面积为 $S$，电荷量为 $q$，定向移动速度为 $v$。
- **黑板板书**：电流微观表达式 $I = nqSv$，推导出导线中共有 $N = nSL$ 个自由电荷。
- **逻辑闭环**：$F_{lorentz} = \\frac{F_{amp}}{N} = \\frac{B(nqSv)L}{nSL} = qvB$。

### 环节三：互动沙盒体验 (10 mins)
- **AI 伴学提示**：请老师打开工作台顶部 **[ 互动游戏 ]** 分区。
- **操作演示**：
  1. 调大磁感应强度 $B$，观察半径 $r$ 如何缩小。
  2. 切换电荷的正负极，验证左手定则。

### 环节四：典例精析与巩固 (10 mins)
**【例题 1】回旋加速器模型**
已知 D 形盒半径为 $R$，磁感应强度为 $B$，质子质量为 $m$，电量为 $q$。求质子能获得的最大动能 $E_{km}$？
- **解析**：当质子从 D 形盒边缘射出时速度最大，此时 $R = \\frac{mv_{max}}{qB}$，得 $v_{max} = \\frac{qBR}{m}$。
- **结果**：$E_{km} = \\frac{1}{2}mv_{max}^2 = \\frac{q^2B^2R^2}{2m}$。

### 环节五：课堂小结 (5 mins)
- 总结洛伦兹力的"三大特点"：**垂直、偏转、不做功**。
`;

export const LORENTZ_DEMO_BLOG_MARKDOWN = `# 🌌 左手定则太难懂？从洛伦兹力到托卡马克核聚变，一篇文章全讲透！

> **作者**：王老师（AI 拟真教学工作台特约物理讲师）| **阅读时长**：约 12 分钟

在高中物理中，带电粒子在磁场中的运动一直是个"老大难"问题。很多同学伸出左手比划了半天，依然搞不清速度 $v$、磁场 $B$ 和洛伦兹力 $F$ 的三维空间关系。今天，王老师不仅要讲清楚这个方向，还要带你看看这个力在现实世界里究竟撬动了哪些"黑科技"。

---

## 一、🔬 从微观推导出发：洛伦兹力是怎么来的？

很多教材直接给出公式 $F = qvB$，但这个公式的来龙去脉更值得深究。

考虑一段通电导线，长度为 $L$，横截面积为 $S$，导线内自由电子的数密度为 $n$，每个电子电量为 $q$，定向移动速度为 $v$。

由安培定律，这段导线受到的宏观安培力为：
$$F_{\\text{安培}} = BIL$$

而其中的微观电流 $I$ 可以表达为：
$$I = nqSv$$

这段导线中共有自由电子 $N = nSL$ 个，因此**每个电子**（即每个运动电荷）平均受到的力为：
$$F_{\\text{洛伦兹}} = \\frac{F_{\\text{安培}}}{N} = \\frac{BIL}{nSL} = \\frac{B(nqSv)L}{nSL} = qvB$$

这正是洛伦兹力公式的微观推导根源——**宏观安培力，正是无数个微观洛伦兹力的矢量合力**。

若速度 $v$ 与磁场 $B$ 方向夹角为 $\\theta$，则一般公式为：
$$\\boxed{F = qvB\\sin\\theta}$$

---

## 二、🌀 带电粒子为什么做圆周运动？

当 $v \\perp B$（即 $\\theta = 90°$）时，洛伦兹力始终与速度垂直，**只改变速度方向，不改变速度大小**。这正是做匀速圆周运动的充要条件：洛伦兹力充当向心力。

由牛顿第二定律可得轨道半径 $r$：
$$qvB = \\frac{mv^2}{r} \\implies \\boxed{r = \\frac{mv}{qB}}$$

进一步推导周期 $T$（这是一个极其反直觉的结论！）：
$$T = \\frac{2\\pi r}{v} = \\frac{2\\pi}{v} \\cdot \\frac{mv}{qB} \\implies \\boxed{T = \\frac{2\\pi m}{qB}}$$

**⚡ 震撼结论**：周期 $T$ 与粒子速度 $v$ 完全无关！无论粒子跑多快，在同一磁场中绕一圈的时间恒定。这个结论是回旋加速器的理论基石。

---

## 三、⚡ 洛伦兹力不做功的数学证明

这一点是最容易被同学忽视的，我们用动能定理来严格证明：

功的定义为 $W = \\vec{F} \\cdot \\vec{\\Delta r}$。由于洛伦兹力 $\\vec{F}$ 始终垂直于位移方向 $\\vec{v}$，所以：
$$W = \\vec{F} \\cdot \\vec{\\Delta r} = F \\cdot |\\Delta r| \\cdot \\cos 90° = 0$$

由动能定理 $W = \\Delta E_k = \\frac{1}{2}mv_2^2 - \\frac{1}{2}mv_1^2 = 0$，即 $v_1 = v_2$。

**洛伦兹力只拐弯，从不加速，也从不减速。**

---

## 四、🚀 三大顶级工程应用

### 4.1 回旋加速器（Cyclotron）
利用周期 $T$ 与速度无关的特性，在两个 D 形盒上施加交变电场，粒子每过间隙被电场加速一次，轨道半径越来越大，最终从边缘射出，获得极高动能。

最大动能推导：当粒子轨道半径等于 D 形盒半径 $R$ 时速度最大，$v_{\\max} = \\frac{qBR}{m}$，因此：
$$\\boxed{E_{k,\\max} = \\frac{1}{2}mv_{\\max}^2 = \\frac{q^2B^2R^2}{2m}}$$

### 4.2 质谱仪（Mass Spectrometer）
不同质量的离子在磁场中轨道半径不同：$r = \\frac{mv}{qB}$，通过测量落点间距，可以精确分离同位素，是核物理与化学分析的核心仪器。

### 4.3 托卡马克（Tokamak）核聚变装置
这是洛伦兹力最"烧脑"的工程应用。托卡马克用强磁场约束数亿度高温的等离子体使其不接触器壁，核心原理正是：带电粒子在螺旋磁场中沿磁力线做螺旋运动，被"磁笼"关住。

磁约束的临界条件（Lawson 判据）涉及粒子密度 $n$、温度 $T$ 与约束时间 $\\tau$ 的乘积：
$$n \\cdot T \\cdot \\tau \\geq 3 \\times 10^{21}\\ \\text{keV} \\cdot \\text{s} \\cdot \\text{m}^{-3}$$

实现这一目标，意味着人类将拥有取之不尽的清洁能源。而这一切，都建立在洛伦兹力 $F = qvB$ 这一朴素方程之上。

---

## 五、🎮 动手体验：AI 拟真沙盒操作指南

王老师在本工作台右侧内置了高精度物理沙盒，打开**【互动游戏】**分区即可体验：

1. **拖动「磁感应强度 B」滑块**：$B$ 越大，轨道半径 $r = \\frac{mv}{qB}$ 越小，粒子转弯越"急"
2. **拖动「初速度 v」滑块**：$v$ 越大，轨道圆越大，但周期 $T = \\frac{2\\pi m}{qB}$ 不变
3. **观察绿色箭头**（速度 $v$，始终切线方向）与**红色箭头**（洛伦兹力 $F$，始终指向圆心）

学习物理，不应只是在草稿纸上推公式，更应该**看见真理在空间中运行的轨迹**。

快去工作台，亲手把粒子的命运握在手中吧！🚀
`;

export const LORENTZ_DEMO_VIDEO_MARKDOWN = '🎬 《洛伦兹力：粒子在磁场中的舞蹈》短视频分镜脚本';

export const LORENTZ_DEMO_ANIMATION_HTML = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue','PingFang SC',sans-serif;background:linear-gradient(160deg,#f0f4ff 0%,#fafbff 100%);min-height:100vh;display:flex;flex-direction:column;align-items:center;padding:14px 12px;gap:12px;overflow-x:hidden}
h2{font-size:13px;font-weight:700;color:#1e293b;letter-spacing:0.3px;text-align:center}
canvas{border-radius:18px;max-width:100%;display:block;box-shadow:0 8px 40px rgba(79,70,229,0.22)}
.info-bar{display:flex;gap:8px;width:100%;max-width:420px}
.chip{flex:1;background:white;border-radius:12px;padding:7px 10px;box-shadow:0 2px 8px rgba(0,0,0,0.05);text-align:center}
.clabel{font-size:10px;font-weight:600;color:#94a3b8;text-transform:uppercase;letter-spacing:0.4px}
.cval{font-size:13px;font-weight:800;color:#1e293b;margin-top:2px}
.controls{width:100%;max-width:420px;display:flex;flex-direction:column;gap:8px}
.row{display:flex;align-items:center;gap:10px;background:white;padding:9px 14px;border-radius:14px;box-shadow:0 2px 12px rgba(0,0,0,0.06)}
label{font-size:12px;font-weight:600;color:#64748b;width:90px;flex-shrink:0}
input[type=range]{flex:1;accent-color:#4f46e5;cursor:pointer}
.val{font-size:12px;font-weight:700;color:#4f46e5;width:58px;text-align:right;flex-shrink:0}
.legend{display:flex;gap:16px;font-size:11px;font-weight:600;color:#64748b}
.leg{display:flex;align-items:center;gap:5px}
.dot{width:10px;height:3px;border-radius:2px}
</style>
</head>
<body>
<h2>⚡ 洛伦兹力 · 带电粒子匀速圆周运动模拟</h2>
<canvas id="c"></canvas>
<div class="info-bar">
  <div class="chip"><div class="clabel">轨道半径 r</div><div class="cval" id="rD">—</div></div>
  <div class="chip"><div class="clabel">洛伦兹力 F</div><div class="cval" id="fD">—</div></div>
  <div class="chip"><div class="clabel">角速度 ω</div><div class="cval" id="wD">—</div></div>
</div>
<div class="controls">
  <div class="row">
    <label>磁场强度 B</label>
    <input type="range" id="bS" min="0.2" max="3.0" step="0.1" value="1.0">
    <span class="val" id="bV">1.0 T</span>
  </div>
  <div class="row">
    <label>初速度 v</label>
    <input type="range" id="vS" min="1" max="10" step="0.5" value="3">
    <span class="val" id="vV">3.0×10⁶</span>
  </div>
</div>
<div class="legend">
  <div class="leg"><div class="dot" style="background:#34d399"></div>速度 v（切线）</div>
  <div class="leg"><div class="dot" style="background:#f87171"></div>洛伦兹力 F（指心）</div>
  <div class="leg"><div class="dot" style="background:#818cf8;width:24px;border:1px dashed #818cf8;background:none"></div>轨道</div>
</div>
<script>
(function(){
var c=document.getElementById('c');
var W=420,H=290;c.width=W;c.height=H;
var ctx=c.getContext('2d');
var m=1.67e-27,q=1.6e-19;
var B=1.0,v=3e6;
var BASE_R=88,BASE_B=1.0,BASE_V=3e6;
var angle=-Math.PI/2,trail=[],MAX_T=300,lastTs=0;
function getR(){var r=(BASE_R*(v/BASE_V))/(B/BASE_B);return Math.max(16,Math.min(W/2-20,r));}
function getOmega(){return 1.4*(B/BASE_B);}
function physics(){
  var rm=(m*v)/(q*B);
  var F=q*v*B;
  var om=q*B/m;
  document.getElementById('rD').textContent=(rm*100).toFixed(2)+' cm';
  document.getElementById('fD').textContent=(F/1e-14).toFixed(2)+'×10⁻¹⁴N';
  document.getElementById('wD').textContent=(om/1e8).toFixed(2)+'×10⁸';
}
function reset(){angle=-Math.PI/2;trail=[];}
document.getElementById('bS').addEventListener('input',function(){B=+this.value;document.getElementById('bV').textContent=B.toFixed(1)+' T';reset();physics();});
document.getElementById('vS').addEventListener('input',function(){v=+this.value*1e6;document.getElementById('vV').textContent=(+this.value).toFixed(1)+'×10⁶';reset();physics();});
physics();
function arrow(x1,y1,x2,y2,col,lbl){
  var dx=x2-x1,dy=y2-y1,a=Math.atan2(dy,dx);
  ctx.beginPath();ctx.moveTo(x1,y1);ctx.lineTo(x2,y2);
  ctx.strokeStyle=col;ctx.lineWidth=2;ctx.stroke();
  ctx.beginPath();ctx.moveTo(x2,y2);
  ctx.lineTo(x2-9*Math.cos(a-0.4),y2-9*Math.sin(a-0.4));
  ctx.lineTo(x2-9*Math.cos(a+0.4),y2-9*Math.sin(a+0.4));
  ctx.closePath();ctx.fillStyle=col;ctx.fill();
  if(lbl){ctx.fillStyle=col;ctx.font='bold 10px -apple-system,sans-serif';ctx.fillText(lbl,x2+5,y2+4);}
}
function frame(ts){
  var dt=Math.min((ts-lastTs)/1000,0.05);lastTs=ts;
  var om=getOmega();angle+=om*dt;
  var R=getR(),CX=W/2,CY=H/2;
  var px=CX+R*Math.cos(angle),py=CY+R*Math.sin(angle);
  trail.push({x:px,y:py});if(trail.length>MAX_T)trail.shift();
  ctx.fillStyle='#0f172a';ctx.fillRect(0,0,W,H);
  ctx.fillStyle='rgba(99,102,241,0.2)';
  for(var gx=16;gx<W;gx+=26)for(var gy=16;gy<H;gy+=26){ctx.beginPath();ctx.arc(gx,gy,1.6,0,Math.PI*2);ctx.fill();}
  ctx.fillStyle='rgba(99,102,241,0.45)';ctx.font='bold 11px -apple-system,sans-serif';ctx.fillText('B ⊙',10,H-10);
  ctx.beginPath();ctx.arc(CX,CY,R,0,Math.PI*2);
  ctx.strokeStyle='rgba(99,102,241,0.18)';ctx.lineWidth=1.5;ctx.setLineDash([5,7]);ctx.stroke();ctx.setLineDash([]);
  ctx.strokeStyle='rgba(148,163,184,0.25)';ctx.lineWidth=1;
  ctx.beginPath();ctx.moveTo(CX,CY);ctx.lineTo(px,py);ctx.setLineDash([3,5]);ctx.stroke();ctx.setLineDash([]);
  ctx.fillStyle='rgba(148,163,184,0.6)';ctx.font='11px -apple-system,sans-serif';
  var mx=(CX+px)/2,my=(CY+py)/2;ctx.fillText('r',(mx+CX)/2-16,(my+CY)/2-4);
  if(trail.length>1){
    for(var i=1;i<trail.length;i++){
      var al=i/trail.length;
      ctx.beginPath();ctx.moveTo(trail[i-1].x,trail[i-1].y);ctx.lineTo(trail[i].x,trail[i].y);
      ctx.strokeStyle='rgba(129,140,248,'+(al*0.72)+')';ctx.lineWidth=1+al*2;ctx.stroke();
    }
  }
  var vax=-Math.sin(angle)*30,vay=Math.cos(angle)*30;
  arrow(px,py,px+vax,py+vay,'#34d399','v');
  var fmag=24,fax=(CX-px)/R*fmag,fay=(CY-py)/R*fmag;
  arrow(px,py,px+fax,py+fay,'#f87171','F');
  var g=ctx.createRadialGradient(px-4,py-4,1,px,py,13);
  g.addColorStop(0,'#c7d2fe');g.addColorStop(0.5,'#6366f1');g.addColorStop(1,'#3730a3');
  ctx.beginPath();ctx.arc(px,py,11,0,Math.PI*2);ctx.fillStyle=g;ctx.fill();
  ctx.strokeStyle='rgba(255,255,255,0.55)';ctx.lineWidth=1.5;ctx.stroke();
  ctx.fillStyle='rgba(255,255,255,0.92)';ctx.font='bold 9px -apple-system,sans-serif';
  ctx.textAlign='center';ctx.fillText('p+',px,py+3.5);ctx.textAlign='left';
  requestAnimationFrame(frame);
}
requestAnimationFrame(function(ts){lastTs=ts;requestAnimationFrame(frame);});
})();
</script>
</body>
</html>`;

export const LORENTZ_DEMO_PPT_RAW = '[{"title":"洛伦兹力","type":"cover","subtitle":"主讲人 | 高中物理示范组"},{"title":"目录","type":"toc","bullets":["1. 洛伦兹力的定义与公式","2. 左手定则判断方向","3. 带电粒子做圆周运动","4. 交互物理动画演示","5. 例题精讲"]},{"title":"洛伦兹力公式","type":"slide","bullets":["F = qvB（v⊥B时取最大值）","方向：左手定则——四指指向v，磁线穿手心，拇指指向F","洛伦兹力始终垂直于速度，不做功"]},{"title":"圆周运动半径推导","type":"slide","bullets":["洛伦兹力提供向心力：qvB = mv²/r","化简得 r = mv/(qB)","r 与速度成正比，与磁场强度成反比"]},{"title":"交互物理动画","type":"slide","subtitle":"🎮 调节滑块，实时观察粒子轨迹","bullets":["拖动 B 滑块：磁场越强，半径越小，转速越快","拖动 v 滑块：速度越大，轨道圆越大","绿色箭头=速度  红色箭头=洛伦兹力"]},{"title":"课堂小结","type":"slide","bullets":["F = qvB，方向由左手定则判断","r = mv/(qB)，ω = qB/m（与速度无关）","应用：回旋加速器、质谱仪、霍尔传感器"]}]';

const LORENTZ_DEMO_PPT_DATA = [
  { title: '洛伦兹力', type: 'cover', subtitle: '主讲人 | 高中物理示范组' },
  { title: '目录', type: 'toc', bullets: ['1. 洛伦兹力的定义与公式', '2. 左手定则判断方向', '3. 带电粒子做圆周运动', '4. 交互物理动画演示', '5. 例题精讲'] },
  { title: '洛伦兹力公式', type: 'slide', bullets: ['F = qvB（v⊥B时取最大值）', '方向：左手定则——四指指向v，磁线穿手心，拇指指向F', '洛伦兹力始终垂直于速度，不做功'] },
  { title: '圆周运动半径推导', type: 'slide', bullets: ['洛伦兹力提供向心力：qvB = mv²/r', '化简得 r = mv/(qB)', 'r 与速度成正比，与磁场强度成反比'] },
  { title: '交互物理动画', type: 'slide', subtitle: '🎮 调节滑块，实时观察粒子轨迹', bullets: ['拖动 B 滑块：磁场越强，半径越小，转速越快', '拖动 v 滑块：速度越大，轨道圆越大', '绿色箭头=速度  红色箭头=洛伦兹力'] },
  { title: '课堂小结', type: 'slide', bullets: ['F = qvB，方向由左手定则判断', 'r = mv/(qB)，ω = qB/m（与速度无关）', '应用：回旋加速器、质谱仪、霍尔传感器'] },
] as const;

const LORENTZ_DEMO_GAME_DATA = [
  { front: '洛伦兹力的大小公式是什么？', back: '当速度方向与磁场方向垂直时，洛伦兹力大小为 F = qvB；一般情况可写成 F = qvBsinθ。' },
  { front: '左手定则如何判断洛伦兹力方向？', back: '让磁感线穿过左手手心，四指指向正电荷速度方向，大拇指所指就是洛伦兹力方向。负电荷方向相反。' },
  { front: '为什么洛伦兹力不做功？', back: '因为洛伦兹力始终垂直于速度方向，只改变速度方向，不改变速度大小，所以不做功。' },
  { front: '带电粒子在匀强磁场中为什么会做圆周运动？', back: '洛伦兹力持续充当向心力，始终把速度方向拉向圆心，因此粒子会沿圆轨道运动。' },
  { front: '轨道半径公式是什么？', back: '由 qvB = mv²/r 可得 r = mv/(qB)。速度越大半径越大，磁场越强半径越小。' },
  { front: '角速度与哪些量有关？', back: '角速度公式为 ω = qB/m，只与电荷量、磁场强度和质量有关，与初速度无关。' },
  { front: '磁场强度 B 增大时，轨道会怎样变化？', back: '在质量、电荷量和速度不变时，半径 r 与 B 成反比，所以 B 增大，轨道会更紧、更小。' },
  { front: '初速度 v 增大时，轨道会怎样变化？', back: '在质量、电荷量和磁场不变时，半径 r 与 v 成正比，所以速度越大，轨道圆越大。' },
] as const;

const resolveSourceFiles = (context: LorentzDemoContext) => (
  context.sourceFiles?.length ? context.sourceFiles : (context.fileNames || []).filter(Boolean)
);

const buildBaseEntry = (context: LorentzDemoContext) => ({
  attachment_ids: context.attachmentIds || [],
  source_files: resolveSourceFiles(context),
  user_requirement: context.userRequirement || '发布会演示模式：洛伦兹力特供版',
  updated_at: new Date().toISOString(),
});

export const isLorentzDemoTarget = ({ projectName, fileNames = [] }: Pick<LorentzDemoContext, 'projectName' | 'fileNames'>) => {
  void fileNames;
  return (projectName || '').includes(LORENTZ_DEMO_KEYWORD);
};

export const getLorentzDemoDelayMs = () => Math.floor(Math.random() * 2001) + 3000;

export const waitForLorentzDemoDelay = (ms: number) => new Promise<void>((resolve) => {
  window.setTimeout(resolve, ms);
});

export const buildLorentzDemoLessonPlanEntry = (context: LorentzDemoContext): GeneratedContentEntry<string> => ({
  format: 'markdown',
  data: LORENTZ_DEMO_LESSON_PLAN_MARKDOWN,
  raw_content: LORENTZ_DEMO_LESSON_PLAN_MARKDOWN,
  ...buildBaseEntry(context),
});

export const buildLorentzDemoPptEntry = (context: LorentzDemoContext): GeneratedContentEntry<readonly unknown[]> => ({
  format: 'json',
  data: LORENTZ_DEMO_PPT_DATA,
  raw_content: LORENTZ_DEMO_PPT_RAW,
  ...buildBaseEntry(context),
});

export const buildLorentzDemoGameEntry = (context: LorentzDemoContext): GeneratedContentEntry<readonly unknown[]> => ({
  format: 'json',
  data: LORENTZ_DEMO_GAME_DATA,
  raw_content: JSON.stringify(LORENTZ_DEMO_GAME_DATA),
  ...buildBaseEntry(context),
});

export const buildLorentzDemoBlogEntry = (context: LorentzDemoContext): GeneratedContentEntry<string> => ({
  format: 'markdown',
  data: LORENTZ_DEMO_BLOG_MARKDOWN,
  raw_content: LORENTZ_DEMO_BLOG_MARKDOWN,
  ...buildBaseEntry(context),
});

export const buildLorentzDemoVideoEntry = (context: LorentzDemoContext): GeneratedContentEntry<string> => ({
  format: 'markdown',
  data: LORENTZ_DEMO_VIDEO_MARKDOWN,
  raw_content: LORENTZ_DEMO_VIDEO_MARKDOWN,
  ...buildBaseEntry(context),
});
