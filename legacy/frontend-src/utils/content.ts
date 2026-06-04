import MarkdownIt from 'markdown-it';
import type {
  GameCardContent,
  GeneratedContentEntry,
  PptSlideContent,
  VideoSceneContent,
} from '../types';

type ContentEntry = GeneratedContentEntry<unknown> | null | undefined;
type SupportedGeneratorType = 'ppt' | 'lesson-plan' | 'video' | 'game' | 'blog';

const markdownRenderer = new MarkdownIt({
  breaks: true,
  html: false,
  linkify: true,
});

const stripWrappedCodeFence = (source: string) => {
  const trimmed = source.trim();
  const fenceMatch = trimmed.match(/^```(?:[\w-]+)?\s*([\s\S]*?)\s*```$/i);
  return fenceMatch ? fenceMatch[1].trim() : trimmed;
};

const isRecord = (value: unknown): value is Record<string, unknown> => (
  typeof value === 'object' && value !== null && !Array.isArray(value)
);

const toNonEmptyString = (value: unknown) => (typeof value === 'string' ? value.trim() : '');

const splitTextToList = (value: string) => (
  value
    .replace(/\r/g, '\n')
    .split(/\n+|[；;]+/)
    .map((item) => item.replace(/^[\-•·▪◦●*]+\s*/, '').replace(/^\d+[.)、．]\s*/, '').trim())
    .filter(Boolean)
);

const toStringList = (value: unknown) => (
  typeof value === 'string'
    ? splitTextToList(value)
    : Array.isArray(value)
      ? value.flatMap((item) => {
          if (typeof item === 'string') {
            return splitTextToList(item);
          }

          if (isRecord(item)) {
            return [
              item.content,
              item.text,
              item.description,
              item.summary,
              item.value,
              item.label,
            ].flatMap((entry) => toStringList(entry));
          }

          return [] as string[];
        })
      : []
);

/**
 * 提取源字符串中所有括号平衡的 [...] 子串，按长度降序排列。
 * 长度越长越可能是完整的 JSON 数组，放在前面优先尝试。
 */
const extractBalancedArrayCandidates = (text: string): string[] => {
  const results: string[] = [];

  for (let start = 0; start < text.length; start++) {
    if (text[start] !== '[') continue;

    let depth = 0;
    let inStr = false;
    let esc = false;

    for (let end = start; end < text.length; end++) {
      const ch = text[end];
      if (esc) { esc = false; continue; }
      if (ch === '\\' && inStr) { esc = true; continue; }
      if (ch === '"') { inStr = !inStr; continue; }
      if (inStr) continue;
      if (ch === '[' || ch === '{') { depth++; }
      else if (ch === ']' || ch === '}') {
        depth--;
        if (depth === 0 && ch === ']') {
          results.push(text.slice(start, end + 1));
          break;
        }
      }
    }
  }

  return results.sort((a, b) => b.length - a.length);
};

const parseJsonArrayFromString = (source: string): unknown[] | null => {
  const normalized = stripWrappedCodeFence(source);

  const tryArr = (candidate: string): unknown[] | null => {
    try {
      const parsed = JSON.parse(candidate.trim());
      return Array.isArray(parsed) ? parsed : null;
    } catch {
      return null;
    }
  };

  // 直接解析（LLM 输出干净时最快）
  const direct = tryArr(normalized);
  if (direct) return direct;

  // 按平衡括号提取所有 [...] 候选，按长度优先尝试最长的
  for (const candidate of extractBalancedArrayCandidates(normalized)) {
    const result = tryArr(candidate);
    if (result) return result;
  }

  return null;
};

const resolveStructuredArray = (entry: ContentEntry) => {
  if (Array.isArray(entry?.data)) {
    const arr = entry.data;
    // 如果是单条假数组（假负性兼容结果），尝试用 raw_content 重解析
    if (arr.length <= 1 && typeof entry.raw_content === 'string' && entry.raw_content.trim()) {
      const reparsed = parseJsonArrayFromString(entry.raw_content);
      if (reparsed && reparsed.length > 1) {
        return reparsed;
      }
    }
    return arr;
  }

  for (const candidate of [entry?.data, entry?.raw_content]) {
    if (typeof candidate !== 'string' || !candidate.trim()) {
      continue;
    }

    const parsed = parseJsonArrayFromString(candidate);
    if (parsed) {
      return parsed;
    }
  }

  return [] as unknown[];
};

const resolvePptBulletCandidates = (item: Record<string, unknown>) => {
  const candidateFields = [
    item.bullets,
    item.content,
    item.contents,
    item.points,
    item.items,
    item.body,
    item.text,
    item.description,
    item.summary,
    item.note,
    item.notes,
    item.keyPoints,
    item.key_points,
    item.highlights,
    item.outline,
    item.details,
  ];

  return Array.from(new Set(candidateFields.flatMap((candidate) => toStringList(candidate))));
};

const buildArrayFallback = (generatorType: SupportedGeneratorType, rawContent: string) => {
  const paragraphs = rawContent
    .split(/\n+/)
    .map((line) => line.trim())
    .filter(Boolean);

  if (generatorType === 'ppt') {
    return (paragraphs.length > 0 ? paragraphs : ['AI 已生成一页初稿内容。']).map((paragraph, index) => ({
      title: `幻灯片 ${index + 1}`,
      bullets: [paragraph],
    }));
  }

  if (generatorType === 'video') {
    return (paragraphs.length > 0 ? paragraphs : ['AI 已生成一段分镜说明。']).map((paragraph, index) => ({
      title: `场景 ${index + 1}`,
      narration: paragraph,
      visuals: [],
    }));
  }

  return (paragraphs.length > 0 ? paragraphs : ['AI 已生成一张知识卡片。']).map((paragraph, index) => ({
    front: `知识卡片 ${index + 1}`,
    back: paragraph,
  }));
};

export const resolveMarkdownSource = (entry: ContentEntry) => {
  const candidate = toNonEmptyString(entry?.data) || toNonEmptyString(entry?.raw_content);
  return candidate ? stripWrappedCodeFence(candidate) : '';
};

export const resolvePptSlides = (entry: ContentEntry): PptSlideContent[] => (
  resolveStructuredArray(entry)
    .map((item, index): PptSlideContent | null => {
      if (!isRecord(item)) {
        return null;
      }

      const bullets = resolvePptBulletCandidates(item);
      const title =
        toNonEmptyString(item.title)
        || toNonEmptyString(item.pageTitle)
        || toNonEmptyString(item.heading)
        || toNonEmptyString(item.name)
        || `幻灯片 ${index + 1}`;
      const rawType = toNonEmptyString(item.type).toLowerCase();
      const type = rawType === 'cover' || rawType === 'toc' || rawType === 'slide' || rawType === 'section' ? rawType : 'slide';
      const subtitle =
        toNonEmptyString(item.subtitle)
        || toNonEmptyString(item.subTitle)
        || toNonEmptyString(item.desc);

      return {
        title,
        type,
        subtitle: subtitle || undefined,
        bullets: bullets.length > 0 ? bullets : (type === 'slide' ? ['AI 已根据文档生成此页内容'] : []),
      } satisfies PptSlideContent;
    })
    .filter((item): item is PptSlideContent => item !== null)
);

export const resolveVideoScenes = (entry: ContentEntry): VideoSceneContent[] => (
  resolveStructuredArray(entry)
    .map((item, index): VideoSceneContent | null => {
      if (!isRecord(item)) {
        return null;
      }

      const visuals = toStringList(item.visuals);
      const narration = toNonEmptyString(item.narration) || 'AI 已根据文档生成此段分镜说明。';
      const title = toNonEmptyString(item.title) || `场景 ${index + 1}`;

      return {
        title,
        narration,
        visuals,
      } satisfies VideoSceneContent;
    })
    .filter((item): item is VideoSceneContent => item !== null)
);

export const resolveGameCards = (entry: ContentEntry): GameCardContent[] => (
  resolveStructuredArray(entry)
    .map((item, index): GameCardContent | null => {
      if (!isRecord(item)) {
        return null;
      }

      const front = toNonEmptyString(item.front) || `知识卡片 ${index + 1}`;
      const back = toNonEmptyString(item.back) || 'AI 已根据文档生成此卡片解释。';

      return {
        front,
        back,
      } satisfies GameCardContent;
    })
    .filter((item): item is GameCardContent => item !== null)
);

export const renderMarkdown = (source: string) => {
  const normalized = stripWrappedCodeFence(source);
  return normalized ? markdownRenderer.render(normalized) : '';
};

export const buildPromptOnlyGenerationPrompt = (
  generatorType: SupportedGeneratorType,
  requirement: string,
  projectName?: string,
) => {
  // 零输入兜底：如果用户什么都没写，自动封装默认指令，确保模型有"任务"可执行
  const finalRequirement =
    requirement.trim() ||
    `请根据项目主题「${projectName || '教学'}」，发挥你的专业能力，自主决策并生成一份结构完整的${generatorType}初稿，不得反问或要求补充信息`;

  const noAskRule = '【强制指令】绝对禁止反问或输出任何商量性文字，必须直接输出完整结果。';
  const ctx = projectName ? `项目「${projectName}」` : '';

  if (generatorType === 'ppt') {
    return (
      `${noAskRule}${ctx}要求：${finalRequirement}。` +
      '只返回严格 JSON 数组。第 1 项必须且仅能是 {"title":"网安基础","type":"cover","subtitle":"王老师 | XX高中"}，课程名称可替换；' +
      '第 2 项必须且仅能是 {"title":"目录大纲","type":"toc","bullets":["..."]}；' +
      '后续正文页必须使用 {"title":"页标题","type":"slide","bullets":["短句1","短句2"]} 格式，且 bullets 只能是短句列表，严禁大段长文；' +
      '总页数必须为 8-12 页，不要输出数组之外的任何内容。'
    );
  }

  if (generatorType === 'video') {
    return (
      `${noAskRule}${ctx}要求：${finalRequirement}。` +
      '只返回严格 JSON 数组，格式为 [{"title":"镜头标题","narration":"旁白","visuals":["画面元素1","画面元素2"]}]，' +
      '不少于 5 项，不要输出数组之外的任何内容。'
    );
  }

  if (generatorType === 'game') {
    return (
      `${noAskRule}${ctx}要求：${finalRequirement}。` +
      '只返回严格 JSON 数组，格式为 [{"front":"卡片正面问题","back":"卡片背面解释"}]，' +
      '不少于 8 项，不要输出数组之外的任何内容。'
    );
  }

  if (generatorType === 'blog') {
    return (
      `${noAskRule}${ctx}要求：${finalRequirement}。` +
      '输出适合直接发布的 Markdown 博文，字数不少于 800 字，' +
      '至少包含 ## 二级标题和 ### 三级标题，不要输出代码块围栏。'
    );
  }

  return (
    `${noAskRule}${ctx}要求：${finalRequirement}。` +
    '输出结构清晰的 Markdown 教案，必须包含教学目标、重难点、教学过程、达学效果评估等标准章节，' +
    '至少包含 ## 二级标题和 ### 三级标题，不要输出代码块围栏。'
  );
};

export const buildGeneratedEntryFromRaw = (
  generatorType: SupportedGeneratorType,
  rawContent: string,
  userRequirement: string,
  attachmentIds: number[] = [],
  sourceFiles: string[] = [],
): GeneratedContentEntry => {
  const cleaned = stripWrappedCodeFence(rawContent);

  if (generatorType === 'lesson-plan' || generatorType === 'blog') {
    return {
      format: 'markdown',
      data: cleaned,
      raw_content: rawContent,
      attachment_ids: attachmentIds,
      source_files: sourceFiles,
      user_requirement: userRequirement,
      updated_at: new Date().toISOString(),
    };
  }

  const parsed = parseJsonArrayFromString(rawContent) ?? buildArrayFallback(generatorType, cleaned);

  return {
    format: 'json',
    data: parsed,
    raw_content: rawContent,
    attachment_ids: attachmentIds,
    source_files: sourceFiles,
    user_requirement: userRequirement,
    updated_at: new Date().toISOString(),
  };
};