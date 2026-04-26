/* global Chart */

const PERIOD_SOURCES = [
  { key: "25.12.8-25.12.14", file: "25.12.8-25.12.14行业热度榜.csv" },
  { key: "25.12.15-25.12.21", file: "25.12.15-25.12.21行业热度榜.csv" },
  { key: "25.12.22-25.12.28", file: "25.12.22-25.12.28行业热度榜.csv" },
  { key: "25.12.29-26.1.4", file: "25.12.29-26.1.4行业热度榜.csv" },
  { key: "26.1.5-26.1.11", file: "26.1.5-26.1.11行业热度榜.csv" },
  { key: "26.1.12-26.1.18", file: "26.1.12-26.1.18行业热度榜.csv" },
  { key: "26.1.19-26.1.25", file: "26.1.19-26.1.25行业热度榜.csv" },
  { key: "26.1.26-26.2.1", file: "26.1.26-26.2.1行业热度榜.csv" },
  { key: "26.2.2-26.2.8", file: "26.2.2-26.2.8行业热度榜.csv" },
  { key: "26.2.9-26.2.15", file: "26.2.9-26.2.15行业热度榜.csv" },
  { key: "26.2.16-26.2.22", file: "26.2.16-26.2.22行业热度榜.csv" },
  { key: "26.2.3-26.3.1", file: "26.2.3-26.3.1行业热度榜.csv" },
  { key: "26.3.2-26.3.8", file: "26.3.2-26.3.8行业热度榜.csv" },
  { key: "26.3.23-26.3.29", file: "26.3.23-26.3.29行业热度榜.csv" },
  { key: "26.3.30-26.4.5", file: "26.3.30-26.4.5行业热度榜.csv" },
];

const CATEGORY_ORDER = [
  "全部",
  "时尚穿搭",
  "美食餐饮",
  "旅行出行",
  "数码科技",
  "兴趣文娱",
  "家居生活",
  "其他",
];

const CATEGORY_PATTERNS = [
  {
    name: "时尚穿搭",
    pattern:
      /穿搭|外套|羽绒服|围巾|毛衣|睡衣|包包|鞋|裙|皮衣|皮草|雪地靴|帽子|内搭|大衣|拉夫劳伦|阿迪|lululemon|lululenmon|lululemon|穿戴甲|美甲|染发|发色|彩妆|妆容|防晒|护手霜|身体乳|洗发水|精油|面霜|裙子/i,
  },
  {
    name: "美食餐饮",
    pattern:
      /美食|家常菜|蛋糕|麻辣烫|寿司|茶姬|一点点|古茗|瑞幸|喜茶|盒马|山姆|奶茶|咖啡|小马糕|鸡翅|排骨|火锅|空气炸锅|草莓|年夜饭|糖醋|西红柿|香椿|牛肉|可乐|腊八粥|饼|饭|菜|茶|果|米|锅包肉|苹果糖|车厘子/i,
  },
  {
    name: "旅行出行",
    pattern:
      /旅游攻略|游玩攻略|旅游|旅行|机场|机票|酒店|迪士尼|长白山|威海|云南|南京|广州|重庆|西安|上海|厦门|长沙|苏州|杭州|景德镇|洛阳|福州|南昌|泉州|大理|东湖|海洋公园|里昂|迪拜|川藏线|新加坡|韩国|贝加尔湖/i,
  },
  {
    name: "数码科技",
    pattern: /手机|平板|macbook|iphone|iPhone|苹果17|OPPO|vivo|华为|mate|reno|find|pocket3|大疆|三星|问界|豆包手机|电脑/i,
  },
  {
    name: "家居生活",
    pattern: /家居|家装|收纳|置物架|漏水|净水器|柜子|纸巾猫|狗|猫|花束|发票|幼儿园|环创|主题墙/i,
  },
  {
    name: "兴趣文娱",
    pattern: /拼豆|逐玉|江湖夜雨十年灯|刘宇宁|舞蹈|儿歌|F1|泡泡玛特|画画|绘画|open claw|OpenClaw|三角洲|小马宝莉|海龟汤|生命树|EXO|演唱会|玉簟秋|小马糕|小马市集|小马糕市集|小马糕999|小马糕码|画法/i,
  },
];

const CATEGORY_LABELS = {
  全部: { zh: "全部", en: "All" },
  时尚穿搭: { zh: "时尚穿搭", en: "Fashion" },
  美食餐饮: { zh: "美食餐饮", en: "Food & Beverage" },
  旅行出行: { zh: "旅行出行", en: "Travel" },
  数码科技: { zh: "数码科技", en: "Tech" },
  兴趣文娱: { zh: "兴趣文娱", en: "Hobbies & Culture" },
  家居生活: { zh: "家居生活", en: "Home & Living" },
  其他: { zh: "其他", en: "Other" },
};

const UI_TEXT = {
  zh: {
    meta: { title: "行业热度 · 数据看板" },
    auth: {
      brandSub: "行业热度 · 选品洞察",
      navOverview: "总览",
      navTrend: "热词趋势",
      navCategory: "类目信号",
      navMerch: "选品建议",
      topSign: "注册",
      topLog: "登录",
      proof: "商户桌面选品入口",
      heroTitle: "让商户一眼知道该上什么货",
      heroCopy: "基于热词趋势、类目信号与选品建议，快速进入一个清晰、可信、可直接执行的商户工作台。",
      ctaLogin: "Log in",
      ctaSign: "Sign in",
      floatScore: "高热类目持续跟踪",
      floatSignalKicker: "本周聚焦",
      floatSignalTitle: "热词与选品建议联动",
      previewChip: "Merchant-ready workspace",
      previewMetricLabel: "热词热度",
      previewTagOne: "趋势判断",
      previewTagTwo: "类目筛选",
      previewTagThree: "选品建议",
      floatActionKicker: "进入后可查看",
      floatActionTitle: "热词榜单、趋势图与建议详情",
      back: "返回",
      registerTitle: "注册新账号",
      registerCopy: "请输入电邮地址、用户名和密码，填入内容后即可进入系统。",
      loginTitle: "登入已有帐号",
      loginCopy: "请输入用户名和密码，填入内容后即可进入系统。",
      email: "电邮地址",
      username: "用户名",
      password: "密码",
      registerSubmit: "注册并进入",
      loginSubmit: "登录并进入",
    },
    sidebar: { aria: "主导航", account: "运营账户", workspace: "Pro 工作区" },
    brand: { sub: "行业热度 · 选品洞察" },
    nav: { label: "目录", aria: "页面", hot: "本周热词榜单", selection: "选品建议", question: "问题提问" },
    header: {
      searchAria: "搜索热词或选品建议",
      searchPlaceholder: "搜索热词、类目、选品建议",
      notifications: "通知",
      report: "本周报表",
    },
    lang: { triggerAria: "切换语言" },
    pageHeading: { hot: "热词洞察", selection: "选品建议", question: "问题提问", detailFallback: "选品详情" },
    question: {
      chip: "互动提问",
      title: "Trend-to-Commerce 问答",
      introLead: "把热词信号转成结构化选品建议。",
      introTagLive: "实时 AI 分析",
      introTagPosts: "帖子与评论样本",
      introTagStructured: "结构化答案",
      studioKicker: "问题工作台",
      studioTitle: "输入你的问题",
      responseKicker: "结果看板",
      responseTitle: "AI 推荐结果",
      noteTitle: "使用方式",
      noteText: "输入问题后，系统会结合已采集的话题帖子、评论样本和模型建议生成结构化答案。问题越具体，返回结果通常越可执行。",
      guideTitle: "怎么提问更有效",
      guideScope: "优先问一个明确话题，或补充商品方向、目标人群、使用场景。",
      guideExample: "例如：'拼豆适合卖什么产品？'、'手机壳在春季更适合推哪些款式？'、'防晒霜推荐里哪些方向更适合学生党？'",
      guideModes: "快速摘要适合先看判断；商品方向适合直接拿建议；详细分析会展开原因、机会和风险。",
      inputLabel: "问题",
      inputPlaceholder: "例如：帮我分析拼豆适合卖什么产品",
      inputHelper: "尽量写出 topic、目标用户、场景或商品目标，例如“面向学生”“送礼场景”“适合上新什么产品”。",
      modeLabel: "模式",
      modeProductIdeas: "商品方向",
      modeQuickSummary: "快速摘要",
      modeDetailed: "详细分析",
      submit: "提交问题",
      empty: "提交问题后，这里会显示轮询到的结果。",
      summaryLabel: "摘要",
      answerLabel: "回答",
      ideasLabel: "商品方向",
      risksLabel: "风险提示",
      idle: "待命",
      enterPrompt: "请输入问题。",
      submitFailed: "提交失败：{message}",
      pollingFailed: "轮询失败：{message}",
      queued: "任务 #{id}：排队中",
      running: "任务 #{id}：生成中",
      succeeded: "任务 #{id}：已完成",
      failed: "任务 #{id}：失败",
      noIdeas: "当前没有返回商品建议",
      noRisks: "当前没有返回明显风险",
      ideaUntitled: "未命名建议",
      ideaCategory: "类别",
      ideaPricing: "价格带",
      ideaWhy: "推荐理由",
      waiting: "任务已提交，正在等待后端返回结果...",
      genericFailure: "任务失败，请检查后端或重新提交。",
    },
    summary: {
      aria: "榜单概览",
      top: "TOP 热词",
      topSub: "榜单第 1 位",
      tracked: "监测词条",
      trackedSub: "本期样本量",
      surge: "热度飙升",
      surgeSub: "标注「搜索飙升」",
      unmatched: "未匹配",
      countValue: "{count} 个",
      surgeFlag: "搜索飙升",
    },
    filters: { title: "内容分类" },
    hot: {
      title: "热词榜单",
      loading: "数据加载中…",
      periodLabel: "SELECT TIME PERIOD",
      periodSelectAria: "切换榜单日期",
      export: "导出榜单",
      tableAria: "本周热词榜单",
      rank: "排名",
      topic: "热词",
      category: "类别",
      index: "搜索指数",
      trend: "热度趋势",
      periodPrefix: "数据周期：{label}",
      comparePrev: " · 对比上期",
      newEntry: "进榜",
      vsLastWeek: "较上周",
      collapseTop10: "收起，仅显示前十",
      expandRest: "展开其余 {count} 条",
      noMatchesQuery: "没有找到与“{query}”相关的热词",
      noMatchesGeneric: "没有找到匹配的热词",
      sparkAria: "查看「{topic}」完整热度趋势",
    },
    selection: {
      chip: "优先动作",
      title: "选品建议",
      noteText:
        "这些值得留意的话题由系统根据历史热词数据筛选。点击卡片可查看话题深度分析与选品建议。",
      forecastLabel: "趋势判断",
      noMatches: "没有找到匹配的选品建议",
    },
    modal: { close: "关闭" },
    detail: {
      back: "返回选品建议",
      searchIndexLabel: "搜索指数",
      searchIndexCaption: "当前建议主题的核心搜索热度",
      categoryLabel: "类别",
      heatLabel: "热度",
      relatedLabel: "关联词",
      snapshotTitle: "关键指标",
      mappedLabel: "建议商品",
      reasonTitle: "选品建议原因",
      productsSection: "📦 商品映射与供货建议",
      strategySection: "💡 执行策略 / 内容策略",
      quickSummary: "建议摘要",
      coreScene: "核心场景",
      targetUser: "重点人群",
      leadPoint: "主打卖点",
      priceHint: "建议价格带",
      riskNote: "供货风险",
      evidence: "趋势依据",
    },
    trend: {
      noHistory: "暂无历史周期",
      rangeSummary: "{start} - {end} · 共 {count} 期榜单",
      modalTitle: "「{topic}」热度趋势",
      tooltipLabel: "搜索指数",
      periodAxis: "榜单周期",
      indexAxis: "搜索指数",
    },
  },
  en: {
    meta: { title: "Industry Heat Dashboard" },
    auth: {
      brandSub: "Industry Heat · Merchandising Insights",
      navOverview: "Overview",
      navTrend: "Trend Board",
      navCategory: "Category Signals",
      navMerch: "Merch Picks",
      topSign: "Sign up",
      topLog: "Log in",
      proof: "Merchant desktop entry",
      heroTitle: "Help merchants know what to launch at a glance",
      heroCopy:
        "Enter a calm, trustworthy workspace built around trend signals, category momentum, and merchandising suggestions that lead directly to action.",
      ctaLogin: "Log in",
      ctaSign: "Sign up",
      floatScore: "High-heat categories under watch",
      floatSignalKicker: "This week",
      floatSignalTitle: "Hot terms linked with merchandising suggestions",
      previewChip: "Merchant-ready workspace",
      previewMetricLabel: "Heat signal",
      previewTagOne: "Forecast",
      previewTagTwo: "Category filter",
      previewTagThree: "Merch picks",
      floatActionKicker: "Inside the workspace",
      floatActionTitle: "Leaderboard, trend charts, and detailed suggestions",
      back: "Back",
      registerTitle: "Create a new account",
      registerCopy: "Enter your email, username, and password to enter the workspace.",
      loginTitle: "Log in to an existing account",
      loginCopy: "Enter your username and password to enter the workspace.",
      email: "Email address",
      username: "Username",
      password: "Password",
      registerSubmit: "Create account and enter",
      loginSubmit: "Log in and enter",
    },
    sidebar: { aria: "Primary navigation", account: "Operations Account", workspace: "Pro Workspace" },
    brand: { sub: "Industry Heat · Merchandising Insights" },
    nav: { label: "Navigation", aria: "Pages", hot: "Hot Terms", selection: "Merch Picks", question: "Question" },
    header: {
      searchAria: "Search hot terms or merchandising suggestions",
      searchPlaceholder: "Search hot terms, categories, suggestions",
      notifications: "Notifications",
      report: "Weekly Report",
    },
    lang: { triggerAria: "Switch language" },
    pageHeading: { hot: "Hot Term Insights", selection: "Merchandising Suggestions", question: "Question", detailFallback: "Suggestion Detail" },
    question: {
      chip: "Interactive Query",
      title: "Ask Trend-to-Commerce",
      introLead: "Turn trend signals into structured product recommendations.",
      introTagLive: "Live AI analysis",
      introTagPosts: "Posts and comments",
      introTagStructured: "Structured answers",
      studioKicker: "Question Studio",
      studioTitle: "Compose your request",
      responseKicker: "Response Dashboard",
      responseTitle: "AI recommendation output",
      noteTitle: "How it works",
      noteText: "After you submit a question, the system combines collected topic posts, comment samples, and saved model suggestions to generate a structured answer. More specific questions usually produce more actionable results.",
      guideTitle: "How to ask better",
      guideScope: "Ask about a clear topic first, or add the product direction, target users, and usage scenario.",
      guideExample: 'Example: "What products fit perler beads?" , "What phone-case styles are better for spring launches?" , or "Which sunscreen directions fit students best?"',
      guideModes: "Quick summary gives you a fast judgment, Product ideas focuses on actionable suggestions, and Detailed analysis expands the reasoning, opportunities, and risks.",
      inputLabel: "Question",
      inputPlaceholder: "For example: Analyze what products are suitable for Perler Beads",
      inputHelper: "Include the topic, audience, scenario, or product goal when possible, such as students, gifting, seasonal launches, or beginner users.",
      modeLabel: "Mode",
      modeProductIdeas: "Product ideas",
      modeQuickSummary: "Quick summary",
      modeDetailed: "Detailed analysis",
      submit: "Submit question",
      empty: "After you submit a question, the polled result will appear here.",
      summaryLabel: "Summary",
      answerLabel: "Answer",
      ideasLabel: "Product Ideas",
      risksLabel: "Risks",
      idle: "Idle",
      enterPrompt: "Please enter a question.",
      submitFailed: "Submit failed: {message}",
      pollingFailed: "Polling failed: {message}",
      queued: "Job #{id}: queued",
      running: "Job #{id}: running",
      succeeded: "Job #{id}: succeeded",
      failed: "Job #{id}: failed",
      noIdeas: "No product ideas returned yet",
      noRisks: "No major risks returned",
      ideaUntitled: "Untitled",
      ideaCategory: "Category",
      ideaPricing: "Pricing",
      ideaWhy: "Why",
      waiting: "The job has been submitted and is waiting for the backend result...",
      genericFailure: "The job failed. Please check the backend or submit again.",
    },
    summary: {
      aria: "Leaderboard summary",
      top: "Top term",
      topSub: "No. 1 on the leaderboard",
      tracked: "Tracked terms",
      trackedSub: "Current sample size",
      surge: "Surging terms",
      surgeSub: 'Flagged as "Search surge"',
      unmatched: "No match",
      countValue: "{count} items",
      surgeFlag: "search surge",
    },
    filters: { title: "Categories" },
    hot: {
      title: "Hot Term Leaderboard",
      loading: "Loading data...",
      periodLabel: "SELECT TIME PERIOD",
      periodSelectAria: "Switch leaderboard period",
      export: "Export",
      tableAria: "Weekly hot term leaderboard",
      rank: "Rank",
      topic: "Term",
      category: "Category",
      index: "Search index",
      trend: "Heat trend",
      periodPrefix: "Period: {label}",
      comparePrev: " · vs previous",
      newEntry: "New",
      vsLastWeek: "vs last week",
      collapseTop10: "Collapse to top 10",
      expandRest: "Show {count} more",
      noMatchesQuery: 'No hot terms found for "{query}"',
      noMatchesGeneric: "No matching hot terms",
      sparkAria: 'View full heat trend for "{topic}"',
    },
    selection: {
      chip: "Priority Action",
      title: "Merchandising Suggestions",
      noteText:
        "These noteworthy topics are selected by the system based on historical hot keyword data. Click the card to view detailed topic analysis and product selection suggestions.",
      forecastLabel: "Forecast",
      noMatches: "No matching merchandising suggestions",
    },
    modal: { close: "Close" },
    detail: {
      back: "Back to Suggestions",
      searchIndexLabel: "Search index",
      searchIndexCaption: "Core search heat for this suggested topic",
      categoryLabel: "Category",
      heatLabel: "Heat",
      relatedLabel: "Related terms",
      snapshotTitle: "Key signals",
      mappedLabel: "Suggested SKU",
      reasonTitle: "Why this suggestion",
      productsSection: "📦 Mapped Products & Sourcing",
      strategySection: "💡 Execution / Content Strategy",
      quickSummary: "Quick view",
      coreScene: "Core scene",
      targetUser: "Target user",
      leadPoint: "Lead selling point",
      priceHint: "PRICE BAND",
      riskNote: "SUPPLY RISK",
      evidence: "Signal source",
    },
    trend: {
      noHistory: "No historical periods yet",
      rangeSummary: "{start} - {end} · {count} periods",
      modalTitle: '"{topic}" heat trend',
      tooltipLabel: "Search index",
      periodAxis: "Leaderboard period",
      indexAxis: "Search index",
    },
  },
};

const DEFAULT_LANG = "zh";
const LANG_STORAGE_KEY = "trend-to-commerce-lang";
const DYNAMIC_TEXT_TRANSLATIONS = window.__DYNAMIC_TEXT_TRANSLATIONS__ || {};
const DYNAMIC_TEXT_TRANSLATION_ENTRIES = Object.entries(DYNAMIC_TEXT_TRANSLATIONS).sort((a, b) => b[0].length - a[0].length);
const DYNAMIC_TEXT_PARTIALS = [
  ["今日金价", "Today's Gold Price"],
  ["金价今日价格", "Today's Gold Price"],
  ["逐玉人物关系图", "Zhu Yu Character Relationship Chart"],
  ["厕所漏水到楼下怎么解决", "How to Fix a Toilet Leak Dripping Downstairs"],
  ["刘文祥麻辣烫怎么点", "How to Order Liu Wenxiang Malatang"],
  ["手机壁纸", "Phone Wallpaper"],
  ["春季穿搭", "Spring Outfits"],
  ["早春穿搭", "Early Spring Outfits"],
  ["穿搭风格", "Style Direction"],
  ["瑞幸咖啡", "Luckin Coffee"],
  ["霸王茶姬", "Chagee"],
  ["泡泡玛特", "Pop Mart"],
  ["家常菜", "Home Cooking"],
  ["寿司郎", "Sushiro"],
  ["拼豆", "Perler Beads"],
  ["手机壳", "Phone Cases"],
  ["生日蛋糕", "Birthday Cakes"],
  ["蛋糕", "Cakes"],
  ["黄金", "Gold"],
  ["金价", "Gold Price"],
  ["美食", "Food"],
  ["逐玉", "Zhu Yu"],
  ["穿搭", "Outfits"],
];

function t(key, vars = {}) {
  const value = key.split(".").reduce((acc, part) => acc?.[part], UI_TEXT[appState.lang] || UI_TEXT[DEFAULT_LANG]);
  if (typeof value !== "string") return key;
  return value.replace(/\{(\w+)\}/g, (_, name) => (vars[name] == null ? "" : String(vars[name])));
}

function translateDynamicString(value) {
  if (typeof value !== "string" || !value) return value;
  if (DYNAMIC_TEXT_TRANSLATIONS[value]) return DYNAMIC_TEXT_TRANSLATIONS[value];

  let next = value;
  next = next.replace(/(\d+)-(\d+)元\/对/g, "RMB $1-$2/pair");
  next = next.replace(/(\d+)-(\d+)元（按克重）/g, "RMB $1-$2 (by gram weight)");
  next = next.replace(/(\d+)-(\d+)元（按含金量区分）/g, "RMB $1-$2 (by gold content)");
  next = next.replace(/(\d+)-(\d+)元/g, "RMB $1-$2");
  next = next.replace(/(\d+)点赞量/g, "$1 likes");
  next = next.replace(/(\d+)个/g, "$1");

  DYNAMIC_TEXT_TRANSLATION_ENTRIES.forEach(([source, target]) => {
    next = next.replaceAll(source, target);
  });

  DYNAMIC_TEXT_PARTIALS.forEach(([source, target]) => {
    next = next.replaceAll(source, target);
  });

  return next;
}

function localized(value) {
  if (value && typeof value === "object" && !Array.isArray(value) && ("zh" in value || "en" in value)) {
    return value[appState.lang] ?? value[DEFAULT_LANG] ?? value.en ?? "";
  }
  return appState.lang === "en" && typeof value === "string" ? translateDynamicString(value) : value;
}

function localizedValues(value) {
  if (typeof value === "string") {
    const translated = translateDynamicString(value);
    return translated && translated !== value ? [value, translated] : [value];
  }
  if (Array.isArray(value)) return value.flatMap(localizedValues);
  if (value && typeof value === "object") {
    if ("zh" in value || "en" in value) return [value.zh, value.en].filter(Boolean);
    return Object.values(value).flatMap(localizedValues);
  }
  return [];
}

function getLocale() {
  return appState.lang === "en" ? "en-US" : "zh-CN";
}

function formatNumber(value) {
  return Number(value).toLocaleString(getLocale());
}

function formatYAxisValue(value) {
  if (appState.lang === "zh") {
    if (value >= 1e8) return `${(value / 1e8).toFixed(1)}亿`;
    if (value >= 1e4) return `${Math.round(value / 1e4)}万`;
    return value;
  }
  return new Intl.NumberFormat("en-US", { notation: "compact", maximumFractionDigits: value >= 1e6 ? 1 : 0 }).format(
    value
  );
}

function getCategoryLabel(category) {
  return CATEGORY_LABELS[category]?.[appState.lang] || category;
}

function getSavedLanguage() {
  try {
    const saved = window.localStorage.getItem(LANG_STORAGE_KEY);
    return saved === "en" || saved === "zh" ? saved : DEFAULT_LANG;
  } catch {
    return DEFAULT_LANG;
  }
}

function updatePageDate() {
  const pageDate = document.getElementById("page-date");
  if (!pageDate) return;
  pageDate.textContent = new Date().toLocaleDateString(getLocale(), {
    year: "numeric",
    month: "long",
    day: "numeric",
    weekday: "long",
  });
}

function renderAuthHeroTitle() {
  const titleEl = document.getElementById("auth-hero-title");
  if (!titleEl) return;
  if (appState.lang === "zh") {
    titleEl.innerHTML = `让商户一眼知道<br><span class="auth-hero-title-accent">该</span>上什么货`;
    return;
  }
  titleEl.textContent = t("auth.heroTitle");
}

function updateRouteHeading() {
  const heading = document.getElementById("page-heading");
  const subtitle = document.getElementById("page-subtitle");
  const pageDate = document.getElementById("page-date");
  const header = document.querySelector(".main-header");
  if (appState.route === "selection-detail") {
    heading.textContent = appState.activeDetailTopic
      ? localized(appState.activeDetailTopic.title)
      : t("pageHeading.detailFallback");
    subtitle.textContent = "";
    subtitle?.setAttribute("hidden", "hidden");
    pageDate?.removeAttribute("hidden");
    header?.classList.remove("main-header-question");
    return;
  }
  if (appState.route === "selection") {
    heading.textContent = t("pageHeading.selection");
    subtitle.textContent = "";
    subtitle?.setAttribute("hidden", "hidden");
    pageDate?.removeAttribute("hidden");
    header?.classList.remove("main-header-question");
    return;
  }
  if (appState.route === "question") {
    heading.textContent = "Ask Trend-to-Commerce";
    subtitle.textContent = appState.lang === "zh"
      ? "把热词信号转成结构化选品建议。"
      : "Turn trend signals into structured product recommendations.";
    subtitle?.removeAttribute("hidden");
    pageDate?.setAttribute("hidden", "hidden");
    header?.classList.add("main-header-question");
    return;
  }
  heading.textContent = t("pageHeading.hot");
  subtitle.textContent = "";
  subtitle?.setAttribute("hidden", "hidden");
  pageDate?.removeAttribute("hidden");
  header?.classList.remove("main-header-question");
}

function updateLanguageMenuState() {
  document.querySelectorAll(".lang-option").forEach((option) => {
    option.classList.toggle("active", option.dataset.lang === appState.lang);
  });
}

function findTopicById(id) {
  const topics = appState.selectionTopics.length ? appState.selectionTopics : buildSelectionTopics();
  return topics.find((topic) => topic.id === id) || null;
}

function setAuthView(view) {
  appState.authView = view;
  document.getElementById("auth-stage-home").classList.toggle("hidden", view !== "home");
  document.getElementById("auth-stage-register").classList.toggle("hidden", view !== "register");
  document.getElementById("auth-stage-login").classList.toggle("hidden", view !== "login");
}

function enterDashboard() {
  appState.authenticated = true;
  document.getElementById("auth-shell").classList.add("hidden");
  document.getElementById("app-shell").classList.remove("hidden");
}

function hasValues(ids) {
  return ids.every((id) => document.getElementById(id).value.trim());
}

function setupAuthFlow() {
  document.querySelectorAll("[data-auth-target]").forEach((button) => {
    button.addEventListener("click", () => setAuthView(button.dataset.authTarget));
  });
  document.getElementById("btn-back-home-from-register").addEventListener("click", () => setAuthView("home"));
  document.getElementById("btn-back-home-from-login").addEventListener("click", () => setAuthView("home"));

  document.getElementById("register-form").addEventListener("submit", (event) => {
    event.preventDefault();
    if (!hasValues(["register-email", "register-username", "register-password"])) return;
    enterDashboard();
  });

  document.getElementById("login-form").addEventListener("submit", (event) => {
    event.preventDefault();
    if (!hasValues(["login-username", "login-password"])) return;
    enterDashboard();
  });
}

function applyStaticTranslations() {
  document.title = t("meta.title");
  document.documentElement.lang = appState.lang === "en" ? "en" : "zh-CN";

  document.querySelectorAll("[data-i18n]").forEach((node) => {
    node.textContent = t(node.dataset.i18n);
  });

  document.querySelectorAll("[data-i18n-placeholder]").forEach((node) => {
    node.setAttribute("placeholder", t(node.dataset.i18nPlaceholder));
  });

  document.querySelectorAll("[data-i18n-aria-label]").forEach((node) => {
    node.setAttribute("aria-label", t(node.dataset.i18nAriaLabel));
  });

  renderAuthHeroTitle();
  updateRouteHeading();
  updatePageDate();
  updateLanguageMenuState();
}

function setLanguage(lang) {
  if (!UI_TEXT[lang] || appState.lang === lang) return;
  appState.lang = lang;

  try {
    window.localStorage.setItem(LANG_STORAGE_KEY, lang);
  } catch {
    // ignore persistence errors in local file contexts
  }

  applyStaticTranslations();
  if (appState.periods.length) {
    renderPeriodOptions();
    updateCurrentPeriod(appState.selectedPeriodKey);
    updateDashboardView();
  }

  if (appState.activeTrendTopic) {
    openTrendModal(appState.activeTrendTopic, buildTrendSeries(appState.activeTrendTopic));
  }
  if (appState.activeDetailTopic && appState.route === "selection-detail") {
    renderDetailPage(appState.activeDetailTopic);
    updateRouteHeading();
    scheduleDetailProductsPanelHeightSync();
  }
}

function categorizeTopic(topic) {
  for (const bucket of CATEGORY_PATTERNS) {
    if (bucket.pattern.test(topic)) return bucket.name;
  }
  return "其他";
}

function formatPeriodLabel(key) {
  const [startRaw, endRaw] = key.split("-");
  const [startYear, startMonth, startDay] = startRaw.split(".").map(Number);
  const [endYear, endMonth, endDay] = endRaw.split(".").map(Number);
  const fullStartYear = startYear < 100 ? 2000 + startYear : startYear;
  const fullEndYear = endYear < 100 ? 2000 + endYear : endYear;
  const start = `${fullStartYear}.${String(startMonth).padStart(2, "0")}.${String(startDay).padStart(2, "0")}`;
  const endSameYear = fullStartYear === fullEndYear;
  const end = endSameYear
    ? `${String(endMonth).padStart(2, "0")}.${String(endDay).padStart(2, "0")}`
    : `${fullEndYear}.${String(endMonth).padStart(2, "0")}.${String(endDay).padStart(2, "0")}`;
  return `${start} - ${end}`;
}

function formatShortPeriodLabel(key) {
  const [startRaw, endRaw] = key.split("-");
  const [, startMonth, startDay] = startRaw.split(".").map(Number);
  const [, endMonth, endDay] = endRaw.split(".").map(Number);
  return `${String(startMonth).padStart(2, "0")}.${String(startDay).padStart(2, "0")} - ${String(endMonth).padStart(2, "0")}.${String(endDay).padStart(2, "0")}`;
}

function periodSortValue(key) {
  const [startRaw] = key.split("-");
  const [year, month, day] = startRaw.split(".").map(Number);
  return new Date(year < 100 ? 2000 + year : year, month - 1, day).getTime();
}

function parseCSV(text) {
  const lines = text.trim().split(/\r?\n/);
  lines.shift();
  const rows = [];
  for (const line of lines) {
    if (!line.trim()) continue;
    const parts = line.split(",");
    if (parts.length < 3) continue;
    const topic = parts[0];
    const index = parseInt(parts[1], 10);
    const surge = parts.slice(2).join(",").trim();
    rows.push({ topic, index, surge, category: categorizeTopic(topic) });
  }
  return rows;
}

function buildRankMap(rows) {
  const map = new Map();
  rows.forEach((r, i) => map.set(r.topic, i + 1));
  return map;
}

function hashStr(s) {
  let h = 2166136261;
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return Math.abs(h);
}

function series30(seed, surgeFlag) {
  const pts = [];
  let v = 0.35 + (seed % 17) / 100;
  const drift = surgeFlag.includes("飙升") ? 0.03 : surgeFlag.includes("--") ? -0.008 : 0.01;
  for (let i = 0; i < 30; i++) {
    const noise = Math.sin(seed * 0.01 + i * 0.7) * 0.06;
    v = Math.min(1, Math.max(0.05, v + drift * 0.05 + noise * 0.02));
    pts.push(v);
  }
  return pts;
}

function sparkPath(points, w, h) {
  const pad = 2;
  const innerW = w - pad * 2;
  const innerH = h - pad * 2;
  let min = Math.min(...points);
  let max = Math.max(...points);
  if (min === max) {
    min -= 0.1;
    max += 0.1;
  }
  const d = points
    .map((p, i) => {
      const x = pad + (i / (points.length - 1)) * innerW;
      const y = pad + innerH - ((p - min) / (max - min)) * innerH;
      return `${i === 0 ? "M" : "L"} ${x.toFixed(2)} ${y.toFixed(2)}`;
    })
    .join(" ");
  return d;
}

let trendChart;

function summarizeArchiveRange(periods) {
  if (!periods.length) return t("trend.noHistory");
  return t("trend.rangeSummary", {
    start: periods[0].label,
    end: periods[periods.length - 1].label,
    count: periods.length,
  });
}

function buildTrendSeries(topic) {
  const labels = appState.periods.map((period) => formatShortPeriodLabel(period.key));
  const values = appState.periods.map((period) => {
    const row = period.rowMap.get(topic);
    return row ? row.index : 0;
  });
  return { labels, values };
}

function openTrendModal(topic, trend) {
  const overlay = document.getElementById("overlay-trend");
  const titleEl = document.getElementById("trend-modal-title");
  const rangeEl = document.getElementById("trend-modal-range");
  appState.activeTrendTopic = topic;
  titleEl.textContent = t("trend.modalTitle", { topic: localized(topic) });
  rangeEl.textContent = summarizeArchiveRange(appState.periods);

  const ctx = document.getElementById("trend-chart").getContext("2d");
  if (trendChart) trendChart.destroy();
  trendChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: trend.labels,
      datasets: [
        {
          data: trend.values,
          borderColor: "#ff6b35",
          backgroundColor: "rgba(255, 107, 53, 0.08)",
          borderWidth: 2,
          tension: 0.24,
          pointRadius: 0,
          pointHoverRadius: 4,
          fill: true,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: "index", intersect: false },
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            title: (items) => items[0].label,
            label: (c) => ` ${t("trend.tooltipLabel")}: ${formatNumber(Math.round(c.parsed.y))}`,
          },
        },
      },
      scales: {
        x: {
          title: {
            display: true,
            text: t("trend.periodAxis"),
            color: "#94a3b8",
            font: { size: 11 },
          },
          grid: { display: true, color: "rgba(148, 163, 184, 0.2)" },
          ticks: { color: "#64748b", maxRotation: 0, autoSkip: true, maxTicksLimit: 9 },
        },
        y: {
          title: {
            display: true,
            text: t("trend.indexAxis"),
            color: "#94a3b8",
            font: { size: 11 },
          },
          grid: { color: "#eef2f7", borderDash: [4, 4] },
          ticks: {
            color: "#64748b",
            callback: (v) => formatYAxisValue(v),
          },
        },
      },
    },
  });

  overlay.classList.add("open");
}

function closeTrendModal() {
  appState.activeTrendTopic = null;
  document.getElementById("overlay-trend").classList.remove("open");
}

function medalForRank(rank) {
  if (rank === 1) return `<span class="medal gold">1</span>`;
  if (rank === 2) return `<span class="medal silver">2</span>`;
  if (rank === 3) return `<span class="medal bronze">3</span>`;
  return `<span class="rank-num">${rank}</span>`;
}

function rankIndicator(rank, topic, prevMap) {
  if (!prevMap.has(topic)) {
    return `<span class="rank-delta new">${t("hot.newEntry")}</span>`;
  }
  const prev = prevMap.get(topic);
  const delta = prev - rank;
  if (delta > 0) {
    return `<span class="rank-delta up" title="${t("hot.vsLastWeek")}">▲ ${delta}</span>`;
  }
  if (delta < 0) {
    return `<span class="rank-delta down" title="${t("hot.vsLastWeek")}">▼ ${Math.abs(delta)}</span>`;
  }
  return `<span class="rank-delta new">—</span>`;
}

const HOT_TABLE_TOP = 10;
const PERIOD_FALLBACKS = window.__HOT_PERIOD_ARCHIVE__ || {};
const DEFAULT_API_BASE = window.location.protocol === "file:" ? "http://127.0.0.1:8000/api" : `${window.location.origin}/api`;
const API_BASE = (window.TREND_TO_COMMERCE_API_BASE || DEFAULT_API_BASE).replace(/\/$/, "");
let detailEntranceTimer = 0;
const appState = {
  apiBase: API_BASE,
  periods: [],
  currentRows: [],
  prevMap: new Map(),
  selectionTopics: [],
  query: "",
  selectedCategory: "全部",
  selectedPeriodKey: "",
  lang: getSavedLanguage(),
  route: "hot",
  activeTrendTopic: null,
  activeDetailTopic: null,
  currentQuestionJobId: null,
  questionPollTimer: 0,
  authenticated: false,
  authView: "home",
};

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

async function detectApiBase() {
  try {
    const response = await fetch(`${appState.apiBase}/health`);
    if (!response.ok) return;
    const payload = await response.json();
    if (!payload.jobs_api) return;
  } catch {
    // The Question page will surface API connection errors when a request is submitted.
  }
}

async function apiFetchJson(path, options) {
  const response = await fetch(`${appState.apiBase}${path}`, options);
  if (!response.ok) {
    let message = `Request failed: ${response.status}`;
    try {
      const payload = await response.json();
      message = payload.detail || payload.error || message;
    } catch {
      message = (await response.text()) || message;
    }
    throw new Error(message);
  }
  return response.json();
}

function matchesHotQuery(row, query) {
  if (!query) return true;
  const q = query.trim().toLowerCase();
  return [...localizedValues(row.topic), row.surge, t("summary.surgeFlag"), row.index, row.category, getCategoryLabel(row.category)]
    .join(" ")
    .toLowerCase()
    .includes(q);
}

function matchesCategory(category) {
  return appState.selectedCategory === "全部" || category === appState.selectedCategory;
}

function renderSummary(rows) {
  const top = rows[0];
  const surgeCount = rows.filter((row) => row.surge.includes("搜索飙升")).length;
  document.getElementById("sum-top").textContent = top ? localized(top.topic) : t("summary.unmatched");
  document.getElementById("sum-count").textContent = formatNumber(rows.length);
  document.getElementById("sum-surge").textContent = t("summary.countValue", { count: formatNumber(surgeCount) });
}

function buildPeriodRecord(meta, csv) {
  const rows = parseCSV(csv).map((row, index) => ({ ...row, rank: index + 1 }));
  return {
    ...meta,
    csv,
    label: formatPeriodLabel(meta.key),
    shortLabel: formatShortPeriodLabel(meta.key),
    rows,
    rowMap: new Map(rows.map((row) => [row.topic, row])),
  };
}

async function loadHotArchive() {
  const periods = await Promise.all(
    PERIOD_SOURCES.map(async (meta) => {
      const embeddedCsv =
        PERIOD_FALLBACKS[meta.key] ||
        (meta.key === "26.3.23-26.3.29" ? window.__HOT_CSV_PREV__ : null) ||
        (meta.key === "26.3.30-26.4.5" ? window.__HOT_CSV_CURRENT__ : null);

      if (embeddedCsv) return buildPeriodRecord(meta, embeddedCsv);

      try {
        const response = await fetch(encodeURI(`../行业热度榜/${meta.file}`));
        if (!response.ok) throw new Error(`Failed to load ${meta.file}`);
        const csv = (await response.text()).trim();
        return csv ? buildPeriodRecord(meta, csv) : null;
      } catch {
        return null;
      }
    })
  );

  const validPeriods = periods.filter(Boolean);
  if (validPeriods.length) return validPeriods.sort((a, b) => periodSortValue(a.key) - periodSortValue(b.key));

  return [
    buildPeriodRecord({ key: "26.3.23-26.3.29", file: "fallback-prev.csv" }, window.__HOT_CSV_PREV__),
    buildPeriodRecord({ key: "26.3.30-26.4.5", file: "fallback-current.csv" }, window.__HOT_CSV_CURRENT__),
  ].sort((a, b) => periodSortValue(a.key) - periodSortValue(b.key));
}

function updateCurrentPeriod(periodKey) {
  const idx = appState.periods.findIndex((period) => period.key === periodKey);
  const safeIndex = idx >= 0 ? idx : appState.periods.length - 1;
  const currentPeriod = appState.periods[safeIndex];
  const prevPeriod = appState.periods[safeIndex - 1];

  appState.selectedPeriodKey = currentPeriod.key;
  appState.currentRows = currentPeriod.rows;
  appState.prevMap = prevPeriod ? buildRankMap(prevPeriod.rows) : new Map();

  const periodLine = `${t("hot.periodPrefix", { label: currentPeriod.label })}${
    prevPeriod ? t("hot.comparePrev") : ""
  }`;
  const hotPeriod = document.getElementById("hot-period");
  if (hotPeriod) hotPeriod.textContent = periodLine;
}

function renderPeriodOptions() {
  const select = document.getElementById("period-select");
  if (!select) return;
  select.innerHTML = appState.periods
    .map(
      (period) =>
        `<option value="${period.key}" ${period.key === appState.selectedPeriodKey ? "selected" : ""}>${period.label}</option>`
    )
    .join("");
}

function escapeCsvCell(value) {
  const text = String(value ?? "");
  return /[",\n]/.test(text) ? `"${text.replace(/"/g, '""')}"` : text;
}

function exportCurrentHotRows() {
  const currentPeriod = appState.periods.find((period) => period.key === appState.selectedPeriodKey);
  if (!currentPeriod) return;

  const headers = [t("hot.rank"), t("hot.topic"), t("hot.category"), t("hot.index")];
  const rows = currentPeriod.rows.slice(0, 100).map((row, index) => [
    row.rank || index + 1,
    localized(row.topic),
    getCategoryLabel(row.category),
    formatNumber(row.index),
  ]);

  const csv = [headers, ...rows].map((line) => line.map(escapeCsvCell).join(",")).join("\n");
  const blob = new Blob([`\uFEFF${csv}`], { type: "text/csv;charset=utf-8;" });
  const link = document.createElement("a");
  const localeTag = appState.lang === "en" ? "en" : "zh";
  const filename = `hot-top100-${currentPeriod.key}-${localeTag}.csv`;

  link.href = URL.createObjectURL(blob);
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(link.href);
}

function renderCategoryFilters(rows) {
  const bar = document.getElementById("category-filter-bar");
  const counts = new Map();
  rows.forEach((row) => counts.set(row.category, (counts.get(row.category) || 0) + 1));

  bar.innerHTML = CATEGORY_ORDER.map((category) => {
    const count = category === "全部" ? rows.length : counts.get(category) || 0;
    return `<button type="button" class="category-filter-btn ${
      appState.selectedCategory === category ? "active" : ""
    }" data-category="${category}">
      <span class="category-filter-name">${getCategoryLabel(category)}</span>
      <span class="category-filter-count">${count}</span>
    </button>`;
  }).join("");

  bar.querySelectorAll(".category-filter-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      appState.selectedCategory = btn.dataset.category;
      updateDashboardView();
    });
  });
}

function renderHotTable(currentRows, prevMap) {
  const tbody = document.getElementById("hot-table-body");
  const shell = document.getElementById("hot-table-shell");
  const panel = document.getElementById("hot-expand-panel");
  const btn = document.getElementById("btn-hot-expand");
  const expandText = document.getElementById("hot-expand-text");

  tbody.innerHTML = "";
  const extraCount = Math.max(0, currentRows.length - HOT_TABLE_TOP);

  const setExpanded = (open) => {
    shell.classList.toggle("hot-table-shell--expanded", open);
    btn.setAttribute("aria-expanded", open ? "true" : "false");
    btn.classList.toggle("is-open", open);
    expandText.textContent = open ? t("hot.collapseTop10") : t("hot.expandRest", { count: extraCount });
  };

  if (!currentRows.length) {
    panel.hidden = true;
    shell.classList.remove("hot-table-shell--expanded");
    tbody.innerHTML = `<tr class="empty-row"><td colspan="5">${
      appState.query
        ? t("hot.noMatchesQuery", { query: escapeHtml(appState.query) })
        : t("hot.noMatchesGeneric")
    }</td></tr>`;
    return;
  }

  if (extraCount > 0) {
    panel.hidden = false;
    setExpanded(false);
    btn.onclick = () => setExpanded(!shell.classList.contains("hot-table-shell--expanded"));
  } else {
    panel.hidden = true;
    shell.classList.remove("hot-table-shell--expanded");
  }

  currentRows.forEach((row, idx) => {
    const rank = row.rank || idx + 1;
    const seed = hashStr(row.topic);
    const gid = `g-${idx}-${seed}`;
    const trend = buildTrendSeries(row.topic);
    const path = sparkPath(trend.values, 100, 32);
    const displayTopic = localized(row.topic);
    const safeTopic = escapeHtml(displayTopic);
    const escTopic = safeTopic;
    const tr = document.createElement("tr");
    if (idx >= HOT_TABLE_TOP) tr.classList.add("hot-row-extra");
    tr.innerHTML = `
      <td>
        <div class="rank-cell">
          ${medalForRank(rank)}
          ${rankIndicator(rank, row.topic, prevMap)}
        </div>
      </td>
      <td>
        <div class="topic-cell">
          <div class="topic-title">${safeTopic}</div>
        </div>
      </td>
      <td>
        <div class="category-cell">
          <span class="category-badge" data-category="${row.category}">${getCategoryLabel(row.category)}</span>
        </div>
      </td>
      <td class="index-val">${formatNumber(row.index)}</td>
      <td>
        <button type="button" class="spark-wrap" aria-label="${t("hot.sparkAria", { topic: escTopic })}">
          <svg class="spark-svg" viewBox="0 0 100 32" aria-hidden="true">
            <defs>
              <linearGradient id="${gid}" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="#ff6b35" stop-opacity="0.38"/>
                <stop offset="100%" stop-color="#ff6b35" stop-opacity="0"/>
              </linearGradient>
            </defs>
            <path class="spark-fill" d="${path} L 100 32 L 0 32 Z" fill="url(#${gid})" opacity="0.95"/>
            <path class="spark-line" d="${path}"/>
          </svg>
          </button>
      </td>`;
    tbody.appendChild(tr);

    const sparkBtn = tr.querySelector(".spark-wrap");
    sparkBtn.addEventListener("click", () => openTrendModal(row.topic, trend));
  });
}

function stopQuestionPolling() {
  if (appState.questionPollTimer) {
    window.clearInterval(appState.questionPollTimer);
    appState.questionPollTimer = 0;
  }
}

function setQuestionStatus(messageKeyOrText, params = {}) {
  const node = document.getElementById("question-job-status");
  if (!node) return;
  const text = messageKeyOrText.includes(".") ? t(messageKeyOrText, params) : messageKeyOrText;
  node.textContent = text;
}

function syncQuestionDefaults() {
  // Leave the input empty by default so the backend can infer the topic from the question text.
}

function renderQuestionResult(result) {
  const empty = document.getElementById("question-result-empty");
  const panel = document.getElementById("question-result");
  const summary = document.getElementById("question-result-summary");
  const answer = document.getElementById("question-result-answer");
  const ideas = document.getElementById("question-result-ideas");
  const risks = document.getElementById("question-result-risks");
  const summaryCard = document.getElementById("question-card-summary");
  const answerCard = document.getElementById("question-card-answer");
  const ideasCard = document.getElementById("question-card-ideas");
  const risksCard = document.getElementById("question-card-risks");
  if (!empty || !panel || !summary || !answer || !ideas || !risks || !summaryCard || !answerCard || !ideasCard || !risksCard) return;

  empty.classList.add("hidden");
  panel.classList.remove("hidden");
  summary.textContent = result.summary || "—";
  answer.textContent = result.answer || "—";

  const displaySections = Array.isArray(result.display_sections) ? result.display_sections : ["summary", "answer", "ideas", "risks"];
  summaryCard.classList.toggle("hidden", !displaySections.includes("summary"));
  answerCard.classList.toggle("hidden", !displaySections.includes("answer"));
  ideasCard.classList.toggle("hidden", !displaySections.includes("ideas"));
  risksCard.classList.toggle("hidden", !displaySections.includes("risks"));

  const productIdeas = result.product_ideas || [];
  ideas.innerHTML = productIdeas.length
    ? productIdeas
        .map(
          (item) => `
        <article class="question-idea-card">
          <h4>${escapeHtml(item.name || t("question.ideaUntitled"))}</h4>
          <p><strong>${t("question.ideaCategory")}:</strong> ${escapeHtml(item.category || "-")}</p>
          <p><strong>${t("question.ideaPricing")}:</strong> ${escapeHtml(item.pricing_hint || "-")}</p>
          <p><strong>${t("question.ideaWhy")}:</strong> ${escapeHtml(item.why || "-")}</p>
        </article>
      `
        )
        .join("")
    : `<div class="selection-empty">${t("question.noIdeas")}</div>`;

  const riskList = result.risk || [];
  risks.innerHTML = riskList.length
    ? riskList.map((risk) => `<span class="question-risk-tag">${escapeHtml(risk)}</span>`).join("")
    : `<span class="question-risk-tag">${t("question.noRisks")}</span>`;
}

async function pollQuestionJob(jobId) {
  stopQuestionPolling();
  appState.questionPollTimer = window.setInterval(async () => {
    try {
      const payload = await apiFetchJson(`/jobs/${jobId}`);
      setQuestionStatus(`question.${payload.status}`, { id: jobId });
      if (payload.status === "succeeded") {
        stopQuestionPolling();
        renderQuestionResult(payload.result || {});
      } else if (payload.status === "failed") {
        stopQuestionPolling();
        renderQuestionResult({
          summary: payload.error_message || t("question.genericFailure"),
          answer: t("question.genericFailure"),
          product_ideas: [],
          risk: [],
        });
      }
    } catch (error) {
      stopQuestionPolling();
      setQuestionStatus("question.pollingFailed", { message: error.message });
      const empty = document.getElementById("question-result-empty");
      if (empty) empty.textContent = t("question.pollingFailed", { message: error.message });
    }
  }, 2000);
}

async function submitQuestion() {
  const questionInput = document.getElementById("question-input");
  const modeSelect = document.getElementById("question-mode-select");
  const empty = document.getElementById("question-result-empty");
  const panel = document.getElementById("question-result");
  if (!questionInput || !modeSelect || !empty || !panel) return;

  const question = questionInput.value.trim();
  if (!question) {
    setQuestionStatus("question.enterPrompt");
    questionInput.focus();
    return;
  }

  stopQuestionPolling();
  empty.classList.remove("hidden");
  panel.classList.add("hidden");
  empty.textContent = t("question.waiting");

  try {
    const payload = await apiFetchJson("/generate-answer", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        question,
        topic: null,
        week: appState.selectedPeriodKey || null,
        mode: modeSelect.value,
        language: appState.lang,
      }),
    });
    appState.currentQuestionJobId = payload.job_id;
    setQuestionStatus("question.queued", { id: payload.job_id });
    pollQuestionJob(payload.job_id);
  } catch (error) {
    setQuestionStatus("question.submitFailed", { message: error.message });
    empty.textContent = t("question.submitFailed", { message: error.message });
  }
}

function setRoute(route) {
  const main = document.querySelector(".main");
  const hot = document.getElementById("page-hot");
  const sel = document.getElementById("page-selection");
  const question = document.getElementById("page-question");
  const detail = document.getElementById("page-selection-detail");
  const n1 = document.querySelector('[data-route="hot"]');
  const n2 = document.querySelector('[data-route="selection"]');
  const n3 = document.querySelector('[data-route="question"]');
  appState.route = route;
  main?.classList.toggle("main--question", route === "question");
  if (route === "selection-detail") {
    hot.classList.add("hidden");
    sel.classList.add("hidden");
    question.classList.add("hidden");
    detail.classList.remove("hidden");
    n1.classList.remove("active");
    n2.classList.add("active");
    n3.classList.remove("active");
    updateRouteHeading();
    if (appState.activeDetailTopic) {
      const nextHash = `#selection-detail/${appState.activeDetailTopic.id}`;
      if (location.hash !== nextHash) location.hash = nextHash;
    }
  } else if (route === "selection") {
    hot.classList.add("hidden");
    sel.classList.remove("hidden");
    question.classList.add("hidden");
    detail.classList.add("hidden");
    n1.classList.remove("active");
    n2.classList.add("active");
    n3.classList.remove("active");
    updateRouteHeading();
    if (location.hash !== "#selection") location.hash = "selection";
  } else if (route === "question") {
    hot.classList.add("hidden");
    sel.classList.add("hidden");
    question.classList.remove("hidden");
    detail.classList.add("hidden");
    n1.classList.remove("active");
    n2.classList.remove("active");
    n3.classList.add("active");
    syncQuestionDefaults();
    updateRouteHeading();
    if (location.hash !== "#question") location.hash = "question";
  } else {
    hot.classList.remove("hidden");
    sel.classList.add("hidden");
    question.classList.add("hidden");
    detail.classList.add("hidden");
    n2.classList.remove("active");
    n3.classList.remove("active");
    n1.classList.add("active");
    updateRouteHeading();
    if (location.hash !== "#hot" && location.hash !== "") location.hash = "hot";
  }
}

const SELECTION_TOPIC_SOURCES = window.__SELECTION_DETAIL_SOURCE__ || [];
const SELECTION_TOPIC_FALLBACK_EMOJI = {
  outfit: "🧥",
  cake: "🍰",
  gold: "✨",
  perler: "🧩",
  "phone-case": "📱",
};

function compactHeatValue(value) {
  if (!Number.isFinite(value) || value <= 0) return "—";
  return `${new Intl.NumberFormat("en-US", { notation: "compact", maximumFractionDigits: 1 }).format(value)}+`;
}

function uniqueSuggestionValues(suggestions, key, limit = 3) {
  const seen = new Set();
  const values = [];
  suggestions.forEach((item) => {
    (item[key] || []).forEach((value) => {
      const normalized = String(value || "").trim();
      if (!normalized || seen.has(normalized) || values.length >= limit) return;
      seen.add(normalized);
      values.push(normalized);
    });
  });
  return values;
}

function summarizePriceRange(suggestions) {
  const numbers = suggestions.flatMap((item) => String(item.pricing_hint || "").match(/\d+(?:\.\d+)?/g) || []).map(Number);
  if (!numbers.length) return "—";
  const min = Math.min(...numbers);
  const max = Math.max(...numbers);
  return min === max ? `${min}元` : `${min}-${max}元`;
}

function pickSuggestionEmoji(sourceId, category = "") {
  if (/蛋糕|甜品/.test(category)) return "🍰";
  if (/手机壳/.test(category)) return "📱";
  if (/黄金|首饰|珠宝/.test(category)) return "✨";
  if (/穿搭|服装|女装|配饰/.test(category)) return "🧥";
  if (/拼豆|图纸|材料包|DIY/.test(category)) return "🧩";
  return SELECTION_TOPIC_FALLBACK_EMOJI[sourceId] || "✦";
}

function findSourceHeatMetrics(source) {
  const terms = source.heatTerms?.length ? source.heatTerms : localizedValues(source.title);
  const matchedRows = appState.currentRows.filter((row) => terms.some((term) => row.topic.includes(term)));
  const topIndex = matchedRows.reduce((best, row) => Math.max(best, Number(row.index) || 0), 0);
  return { topIndex, label: compactHeatValue(topIndex) };
}

function buildReasonFromSource(source) {
  const focus = source.suggestions
    .slice(0, 3)
    .map((item) => item.category)
    .filter(Boolean)
    .join("、");
  const focusEn = source.suggestions
    .slice(0, 3)
    .map((item) => translateDynamicString(item.category))
    .filter(Boolean)
    .join(", ");
  return {
    zh: `${source.summary.zh} 当前建议重点聚焦 ${focus} 等方向，优先选择高互动场景、明确人群和能被内容反复展示的商品组合。`,
    en: `${source.summary.en} The current recommendation set centers on ${focusEn}, with the clearest upside in scene-driven products, explicit user groups, and repeatable content hooks.`,
  };
}

function buildStrategyFromSource(source) {
  const leadScene = uniqueSuggestionValues(source.suggestions, "use_scenarios", 2).join("、") || "高频场景";
  const topPoint = source.suggestions[0]?.selling_points?.[0] || "明确卖点";
  const firstRisk = source.suggestions[0]?.risk_note || "供货与描述一致性";
  return {
    zh: `内容上先围绕${leadScene}做首屏表达，再把「${topPoint}」这类具体卖点前置；供货侧需要把${firstRisk}提前说清，页面里保持清楚的价格带和适用人群对比。`,
    en: "Lead with the clearest user scene, then move the most concrete selling point into the first screen. Keep price bands, fit, materials, and sourcing constraints explicit so the recommendation feels calm and trustworthy.",
  };
}

function buildSelectionTopics() {
  const topics = SELECTION_TOPIC_SOURCES.map((source) => {
    const leadUsers = uniqueSuggestionValues(source.suggestions, "target_users", 2).join(" / ") || "—";
    const leadScenes = uniqueSuggestionValues(source.suggestions, "use_scenarios", 2).join(" / ") || "—";
    const heatMetrics = findSourceHeatMetrics(source);
    return {
      id: source.id,
      category: source.suggestions[0]?.category || localized(source.subtitle),
      heat: heatMetrics.label,
      heatScore: heatMetrics.topIndex,
      title: source.title,
      subtitle: source.subtitle,
      desc: source.summary,
      forecast: source.forecast,
      tags: source.keywords,
      quote: source.quote,
      reason: buildReasonFromSource(source),
      stats: [
        {
          k: { zh: "建议商品", en: "Suggested SKUs" },
          v: { zh: `${source.suggestions.length} 个`, en: `${source.suggestions.length}` },
        },
        { k: { zh: "主力人群", en: "Lead users" }, v: leadUsers },
        { k: { zh: "价格带", en: "Price band" }, v: summarizePriceRange(source.suggestions) },
      ],
      products: source.suggestions.map((item) => ({
        emoji: pickSuggestionEmoji(source.id, item.category),
        name: item.product_name,
        sub: item.why_recommended,
        category: item.category,
        targetUsers: item.target_users,
        scenarios: item.use_scenarios,
        sellingPoints: item.selling_points,
        evidence: item.evidence,
        priceHint: item.pricing_hint,
        riskNote: item.risk_note,
        leadScenes,
      })),
      strategy: buildStrategyFromSource(source),
    };
  });
  topics.sort((a, b) => (b.heatScore || 0) - (a.heatScore || 0));
  return topics;
}

function sparkForCard(seed) {
  const pts = series30(seed, "飙升");
  return sparkPath(pts, 300, 56);
}

function selectionTopicCategory(topic) {
  return categorizeTopic(
    [
      ...localizedValues(topic.title),
      ...localizedValues(topic.subtitle),
      topic.category,
      ...localizedValues(topic.desc),
      ...topic.tags.flatMap((item) => localizedValues(item.label)),
      ...topic.products.flatMap((item) => [
        ...localizedValues(item.name),
        ...localizedValues(item.sub),
        item.category,
        item.priceHint,
        item.riskNote,
        ...(item.targetUsers || []),
        ...(item.scenarios || []),
        ...(item.sellingPoints || []),
        ...(item.evidence || []),
      ]),
    ].join(" ")
  );
}

function matchesSelectionQuery(topic, query) {
  if (!query) return true;
  const q = query.trim().toLowerCase();
  const haystack = [
    ...localizedValues(topic.title),
    ...localizedValues(topic.subtitle),
    topic.category,
    getCategoryLabel(selectionTopicCategory(topic)),
    ...localizedValues(topic.desc),
    ...localizedValues(topic.forecast),
    ...localizedValues(topic.reason),
    ...localizedValues(topic.quote),
    ...topic.tags.flatMap((item) => localizedValues(item.label)),
    ...topic.products.flatMap((item) => [
      ...localizedValues(item.name),
      ...localizedValues(item.sub),
      item.category,
      item.priceHint,
      item.riskNote,
      ...(item.targetUsers || []),
      ...(item.scenarios || []),
      ...(item.sellingPoints || []),
      ...(item.evidence || []),
    ]),
  ]
    .join(" ")
    .toLowerCase();
  return haystack.includes(q);
}

function renderSelectionCards(query = "") {
  const grid = document.getElementById("selection-grid");
  grid.innerHTML = "";
  const filteredTopics = appState.selectionTopics.filter(
    (topic) => matchesSelectionQuery(topic, query) && matchesCategory(selectionTopicCategory(topic))
  );

  if (!filteredTopics.length) {
    grid.innerHTML = `<div class="card card-pad selection-empty">${t("selection.noMatches")}</div>`;
    return;
  }

  filteredTopics.forEach((topic, i) => {
    const seed = hashStr(topic.id) + i * 17;
    const path = sparkForCard(seed);
    const bucket = selectionTopicCategory(topic);
    const title = localized(topic.title);
    const subtitle = localized(topic.subtitle);
    const desc = localized(topic.desc);
    const forecast = localized(topic.forecast);
    const card = document.createElement("article");
    card.className = "topic-card";
    card.type = "button";
    card.innerHTML = `
      <div class="cat">${getCategoryLabel(bucket)}</div>
      <div class="head-row">
        <h3>${title}${subtitle ? ` <span style="font-size:14px;color:#64748b;font-weight:500">${
          appState.lang === "zh" ? `（${subtitle}）` : `(${subtitle})`
        }</span>` : ""}</h3>
        <div class="heat-pill">🔥 ${topic.heat}</div>
      </div>
      <p class="desc">${desc}</p>
      <div class="forecast-row">
        <span>${t("selection.forecastLabel")}</span>
        <span class="forecast-val">${forecast}</span>
      </div>
      <div class="spark-area">
        <svg viewBox="0 0 300 56" preserveAspectRatio="none">
          <defs>
            <linearGradient id="cardg${seed}" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stop-color="#ea580c" stop-opacity="0.35"/>
              <stop offset="100%" stop-color="#ea580c" stop-opacity="0"/>
            </linearGradient>
          </defs>
          <path d="${path} L 300 56 L 0 56 Z" fill="url(#cardg${seed})" stroke="none"/>
          <path d="${path}" fill="none" stroke="#c2410c" stroke-width="2" stroke-linecap="round"/>
        </svg>
      </div>
      <div class="tags">
        ${topic.tags.map((item) => `<span class="tag">${item.emoji} ${localized(item.label)}</span>`).join("")}
      </div>
      <div class="card-footer-btn">
        <span class="circle-btn" aria-hidden="true">↗</span>
      </div>`;
    card.addEventListener("click", () => openDetailModal(topic));
    grid.appendChild(card);
  });
}

function renderDetailPage(topic) {
  const title = localized(topic.title);
  const subtitle = localized(topic.subtitle);
  const category = selectionTopicCategory(topic);
  const categoryLabel = getCategoryLabel(category);
  const tags = topic.tags.map((item) => `${item.emoji} ${localized(item.label)}`);
  document.getElementById("detail-title").textContent = subtitle
    ? `${title}${appState.lang === "zh" ? `（${subtitle}）` : ` (${subtitle})`}`
    : title;
  document.getElementById("detail-desc").textContent = localized(topic.desc);
  document.getElementById("detail-quote").textContent = localized(topic.quote) || localized(topic.reason);
  document.getElementById("detail-search-index").textContent = topic.heat;
  document.getElementById("detail-category").textContent = categoryLabel;
  document.getElementById("detail-forecast").textContent = localized(topic.forecast);
  document.getElementById("detail-category-badge").textContent = categoryLabel;
  document.getElementById("detail-category-badge").setAttribute("data-category", category);

  const relatedTags = document.getElementById("detail-related-tags");
  relatedTags.innerHTML = tags.map((label) => `<span class="tag">${label}</span>`).join("");

  const stats = document.getElementById("detail-stats");
  stats.innerHTML = topic.stats
    .map(
      (stat) =>
        `<div class="mini-stat"><div class="lbl">${localized(stat.k)}</div><div class="big">${localized(stat.v)}</div></div>`
    )
    .join("");

  const pg = document.getElementById("detail-products");
  pg.innerHTML = topic.products
    .map((product, index) => {
      const chips = [...(product.targetUsers || []).slice(0, 2), ...(product.scenarios || []).slice(0, 2)].slice(0, 4);
      const points = (product.sellingPoints || []).slice(0, 3);
      const evidence = product.evidence?.[0];
      const coreScene = product.scenarios?.[0] || "—";
      const targetUser = product.targetUsers?.[0] || "—";
      const leadPoint = points[0] || localized(product.category) || "—";
      return `
    <div class="product-row">
      <div class="product-emoji">${product.emoji}</div>
      <div class="product-main">
        <div class="product-top">
          <span class="product-label">${t("detail.mappedLabel")} ${String(index + 1).padStart(2, "0")}</span>
          <span class="product-category">${escapeHtml(localized(product.category))}</span>
        </div>
        <strong>${escapeHtml(localized(product.name))}</strong>
        <p class="product-why">${escapeHtml(localized(product.sub))}</p>
        ${
          chips.length
            ? `<div class="product-chip-row">${chips
                .map((chip) => `<span class="product-chip">${escapeHtml(localized(chip))}</span>`)
                .join("")}</div>`
            : ""
        }
        ${
          points.length
            ? `<ul class="product-point-list">${points
                .map((point) => `<li>${escapeHtml(localized(point))}</li>`)
                .join("")}</ul>`
            : ""
        }
        ${
          evidence
            ? `<p class="product-evidence"><span>${t("detail.evidence")}</span>${escapeHtml(localized(evidence))}</p>`
            : ""
        }
      </div>
      <div class="price-box">
        <div class="product-side-kicker">${t("detail.quickSummary")}</div>
        <div class="product-side-title">${escapeHtml(localized(product.category) || "—")}</div>
        <div class="product-side-grid">
          <div class="product-side-item">
            <span>${t("detail.coreScene")}</span>
            <strong>${escapeHtml(localized(coreScene))}</strong>
      </div>
          <div class="product-side-item">
            <span>${t("detail.targetUser")}</span>
            <strong>${escapeHtml(localized(targetUser))}</strong>
          </div>
        </div>
        <div class="product-side-note">
          <span>${t("detail.leadPoint")}</span>
          <p>${escapeHtml(localized(leadPoint))}</p>
        </div>
      </div>
    </div>`;
    })
    .join("");

  document.getElementById("detail-strategy").textContent = localized(topic.strategy);
}

function syncDetailProductsPanelHeight() {
  const productsPanel = document.getElementById("detail-products-panel");
  const statsPanel = document.getElementById("detail-stats-panel");
  const productGrid = document.getElementById("detail-products");
  const sectionTitle = productsPanel?.querySelector(".section-title");
  if (!productsPanel || !statsPanel || !productGrid) return;

  if (appState.route !== "selection-detail" || window.innerWidth <= 1100) {
    productsPanel.style.removeProperty("height");
    productGrid.style.removeProperty("maxHeight");
    return;
  }

  productsPanel.style.removeProperty("height");
  const panelRect = productsPanel.getBoundingClientRect();
  const statsRect = statsPanel.getBoundingClientRect();
  const nextHeight = Math.max(Math.floor(statsRect.bottom - panelRect.top), 320);

  productsPanel.style.height = `${nextHeight}px`;

  const titleStyles = sectionTitle ? window.getComputedStyle(sectionTitle) : null;
  const titleHeight = sectionTitle
    ? sectionTitle.getBoundingClientRect().height + parseFloat(titleStyles?.marginBottom || "0")
    : 0;
  const panelStyles = window.getComputedStyle(productsPanel);
  const paddingTop = parseFloat(panelStyles.paddingTop || "0");
  const paddingBottom = parseFloat(panelStyles.paddingBottom || "0");
  const nextGridHeight = Math.max(Math.floor(nextHeight - titleHeight - paddingTop - paddingBottom), 180);
  productGrid.style.maxHeight = `${nextGridHeight}px`;
}

function scheduleDetailProductsPanelHeightSync() {
  requestAnimationFrame(() => {
    requestAnimationFrame(syncDetailProductsPanelHeight);
  });
}

function playDetailEntranceAnimation() {
  const detailPage = document.getElementById("page-selection-detail");
  if (!detailPage) return;

  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    if (detailEntranceTimer) window.clearTimeout(detailEntranceTimer);
    detailPage.classList.remove("detail-entering");
    return;
  }

  if (detailEntranceTimer) window.clearTimeout(detailEntranceTimer);
  detailPage.classList.remove("detail-entering");
  void detailPage.offsetWidth;
  detailPage.classList.add("detail-entering");

  detailEntranceTimer = window.setTimeout(() => {
    if (appState.route === "selection-detail") {
      detailPage.classList.remove("detail-entering");
    }
    detailEntranceTimer = 0;
  }, 900);
}

function openDetailModal(topic) {
  appState.activeDetailTopic = topic;
  renderDetailPage(topic);
  setRoute("selection-detail");
  scheduleDetailProductsPanelHeightSync();
  requestAnimationFrame(playDetailEntranceAnimation);
}

function closeDetailModal() {
  setRoute("selection");
}

function updateDashboardView() {
  appState.selectionTopics = buildSelectionTopics();
  if (appState.route === "selection-detail" && appState.activeDetailTopic) {
    const next = appState.selectionTopics.find((topic) => topic.id === appState.activeDetailTopic.id);
    if (!next) {
      appState.activeDetailTopic = null;
      if (location.hash.startsWith("#selection-detail/")) {
        location.hash = "#selection";
      }
      setRoute("selection");
    } else {
      appState.activeDetailTopic = next;
      renderDetailPage(next);
      scheduleDetailProductsPanelHeightSync();
    }
  }
  renderCategoryFilters(appState.currentRows);
  const filteredHotRows = appState.currentRows.filter(
    (row) => matchesHotQuery(row, appState.query) && matchesCategory(row.category)
  );
  renderSummary(filteredHotRows);
  renderHotTable(filteredHotRows, appState.prevMap);
  renderSelectionCards(appState.query);
}

function setupLanguageSwitcher() {
  const switchers = [...document.querySelectorAll(".lang-switch")];

  switchers.forEach((switcher) => {
    const trigger = switcher.querySelector(".lang-trigger");
    const menu = switcher.querySelector(".lang-menu");
    if (!trigger || !menu) return;

    const closeMenu = () => {
      menu.hidden = true;
      trigger.setAttribute("aria-expanded", "false");
    };

    const openMenu = () => {
      switchers.forEach((item) => {
        const itemTrigger = item.querySelector(".lang-trigger");
        const itemMenu = item.querySelector(".lang-menu");
        if (itemMenu && itemTrigger) {
          itemMenu.hidden = true;
          itemTrigger.setAttribute("aria-expanded", "false");
        }
      });
      menu.hidden = false;
      trigger.setAttribute("aria-expanded", "true");
    };

    trigger.addEventListener("click", (event) => {
      event.stopPropagation();
      if (menu.hidden) openMenu();
      else closeMenu();
    });

    menu.querySelectorAll(".lang-option").forEach((option) => {
      option.addEventListener("click", () => {
        setLanguage(option.dataset.lang);
        closeMenu();
      });
    });

    document.addEventListener("click", (event) => {
      if (!switcher.contains(event.target)) closeMenu();
    });

    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape") closeMenu();
    });
  });
}

async function boot() {
  setupAuthFlow();
  setAuthView("home");
  applyStaticTranslations();
  setupLanguageSwitcher();
  await detectApiBase();
  appState.periods = await loadHotArchive();
  appState.selectedPeriodKey = appState.periods[appState.periods.length - 1].key;
  updateCurrentPeriod(appState.selectedPeriodKey);
  renderPeriodOptions();

  updateDashboardView();

  document.getElementById("period-select").addEventListener("change", (e) => {
    updateCurrentPeriod(e.target.value);
    updateDashboardView();
  });

  document.getElementById("btn-hot-export").addEventListener("click", exportCurrentHotRows);

  document.querySelectorAll(".nav-item[data-route]").forEach((n) => {
    n.addEventListener("click", () => setRoute(n.dataset.route));
  });

  document.getElementById("btn-question-submit").addEventListener("click", submitQuestion);
  setQuestionStatus("question.idle");

  window.addEventListener("hashchange", () => {
    const h = location.hash.replace("#", "");
    if (h.startsWith("selection-detail/")) {
      const topic = findTopicById(h.split("/")[1]);
      if (topic) openDetailModal(topic);
      else setRoute("selection");
    } else if (h === "selection") setRoute("selection");
    else if (h === "question") setRoute("question");
    else setRoute("hot");
  });
  if (location.hash.startsWith("#selection-detail/")) {
    const topic = findTopicById(location.hash.replace("#selection-detail/", ""));
    if (topic) openDetailModal(topic);
    else setRoute("selection");
  } else if (location.hash === "#selection") {
    setRoute("selection");
  } else if (location.hash === "#question") {
    setRoute("question");
  }

  document.getElementById("overlay-trend").addEventListener("click", (e) => {
    if (e.target.id === "overlay-trend") closeTrendModal();
  });
  document.getElementById("btn-close-trend").addEventListener("click", closeTrendModal);
  document.getElementById("btn-back-selection").addEventListener("click", closeDetailModal);
  window.addEventListener("resize", scheduleDetailProductsPanelHeightSync);
}

window.addEventListener("DOMContentLoaded", boot);
