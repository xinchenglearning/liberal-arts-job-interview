---
name: "liberal-arts-job-interview"
description: "Use when liberal-arts students prepare campus recruiting interviews for product, operations, marketing, procurement, planning, research, sales, HR, publicity, customer success, public-sector, or business roles."
---

# 文科生求职

## 核心定位

本 Skill 只服务文科生及商科、社科等非技术类岗位的校招面试准备。目标不是生成大量通用题库，而是基于目标行业、公司、岗位、JD、简历/项目经历、面试轮次和外部信息，生成聚焦、高质量、可追问的校招面试题；用户确认题目后，再生成结构化答案。

校招的第一性原理：面试官不是要求候选人已经具备社招级完整业务闭环，而是在验证候选人是否真实、靠谱、有潜力、能学习、能讲清楚经历、理解岗位和行业，并具备进入组织后成长的基础。

本地方法论知识库只负责兜底：补充岗位能力框架、常见指标、追问角度和答案结构。用户提供的 JD、简历和项目事实始终优先；公司和行业事实必须来自外部研究。知识库不得替代用户事实，也不得把通用方法论包装成用户经历。

## 启动提问

使用本 Skill 前，必须先向用户收集信息。不要直接生成题目。

```text
请先提供以下信息，越完整题目越贴合：

1. 目标岗位：
2. 目标公司/行业：
3. 组织类型：互联网 / 央国企 / 事业单位 / 制造业 / 快消零售 / 金融 / 咨询专业服务 / 教育医疗 / 其他
4. JD 或岗位描述：没有 JD 可只写岗位方向
5. 面试轮次：HR 面 / 业务面 / 终面 / 不确定
6. 简历或项目经历：可粘贴完整简历，也可只贴目标项目
7. 最想强化的方向：自我介绍 / 简历深挖 / 业务理解 / 指标表达 / AI 认知 / 反问 / 综合匹配
```

若用户信息不足，先标记信息缺口；不要编造公司业务、项目指标或用户经历。

## 行业路由

本 Skill 的路由目标是根据用户提供的信息识别行业/组织场景，从而选择对应行业提示词，让题目更有业务针对性。

优先级：

1. 用户明确写出的行业或组织类型。
2. 用户给出的公司、产品或业务方向。
3. JD 中的高频关键词。
4. 简历项目所属行业。
5. 信息不足时使用 `general_campus`。

主路由：

| 路由 | 触发关键词 |
|---|---|
| `internet` | 互联网、平台、电商、内容、社区、本地生活、搜索、推荐、广告、增长、运营、产品、用户 |
| `state_owned` | 央企、国企、能源、电网、运营商、烟草、铁路、航司、国有银行、政策、合规稳健 |
| `public_institution` | 事业单位、机关、学校、医院、政务、公共服务、公文、编制 |
| `manufacturing` | 制造、工业、汽车、半导体、硬件、供应链、工厂、生产、质量、交付、设备 |
| `fmcg_retail` | 快消、零售、品牌、渠道、门店、消费者、新品、动销、货架、营销 |
| `finance` | 银行、证券、保险、基金、支付、风控、信贷、财富管理、投研 |
| `consulting_professional` | 咨询、战略、研究、审计、法律、投行、FA、专业服务、客户项目 |
| `education_healthcare` | 教育、教培、课程、医疗、药企、健康、患者、医生、学习效果 |
| `general_campus` | 信息不足或无法判断行业 |

AI 不默认作为行业主路由。只有目标岗位本身是 AI 岗、AI 公司，或 JD/用户目标明显涉及 AI、大模型、智能化、算法、Agent、自动化时，才叠加 `ai_business_enhancer`。

## 岗位与知识库路由

行业路由回答“在哪种业务语境中出题”，岗位路由回答“用哪套能力方法论补充问题”。两者必须分别判断：

```text
用户信息
→ 行业路由：互联网 / 央国企 / 制造业 / 快消 / 金融等
→ 岗位路由：产品 / 运营 / 市场 / 采购 / 策划 / 用研 / 销售 / 人力 / 宣传行政 / 客户成功
→ 用户证据矩阵
→ 岗位基础库 + 行业覆盖库
→ 只对证据缺口使用知识库
```

先调用 `research_guard.py` 得到 `industry_route`，再把它与用户输入一起交给：

```bash
python scripts/role_router.py --input user_input.json
```

岗位判断优先级：

1. 用户明确提供的岗位名称。
2. JD 中的职责、交付物和能力关键词。
3. 简历经历只作辅助，不能反向改变目标岗位。
4. 复合岗位最多选择一个主岗位和一个辅助岗位。
5. 无法识别时不强行加载知识库，直接依据 JD 和简历出题。

| 岗位路由 | 知识库 | 核心补充 |
|---|---|---|
| `product` | `knowledge_base/product_methodology.md` | 用户需求、方案设计、优先级、交付、验证 |
| `operations` | `knowledge_base/operations_methodology.md` | 人群分层、运营抓手、执行节奏、留存与复盘 |
| `marketing` | `knowledge_base/marketing_methodology.md` | 消费者洞察、定位、内容渠道、品牌与生意结果 |
| `procurement` | `knowledge_base/procurement_methodology.md` | 需求澄清、寻源、供应商、总成本、交付与合规 |
| `planning` | `knowledge_base/planning_methodology.md` | 目标受众、创意机制、资源排期、执行与效果 |
| `user_research` | `knowledge_base/user_research_methodology.md` | 研究问题、样本方法、证据质量、洞察与落地 |
| `sales_bd` | `knowledge_base/sales_bd_methodology.md` | 客户开发、商机、方案价值、谈判与回款 |
| `human_resources` | `knowledge_base/human_resources_methodology.md` | 招聘、培养、组织、绩效与员工关系 |
| `administration_publicity` | `knowledge_base/administration_publicity_methodology.md` | 材料、宣传、企业文化、舆情、行政协同 |
| `customer_success_project` | `knowledge_base/customer_success_project_methodology.md` | 上线交付、客户采用、项目风险、续约扩容 |

行业覆盖库：

| 行业路由 | 覆盖库 | 重点 |
|---|---|---|
| `internet` | `industry_internet.md` | 用户链路、平台生态、增长与治理 |
| `state_owned` | `industry_state_owned.md` | 使命、组织协同、稳健合规、社会责任 |
| `public_institution` | `industry_public_institution.md` | 公共服务、程序、公平、群众视角 |
| `manufacturing` | `industry_manufacturing.md` | 安全、质量、成本、交付、现场 |
| `fmcg_retail` | `industry_fmcg_retail.md` | 消费者、品牌、渠道、动销、复购 |
| `finance` | `industry_finance.md` | 风险、合规、客户价值与信任 |
| `consulting_professional` | `industry_consulting_professional.md` | 研究、客户项目、证据与交付 |
| `education_healthcare` | `industry_education_healthcare.md` | 效果、专业责任、安全与伦理 |

知识库使用规则：

- 仅补充 `competency_framework`、`role_metrics`、`followup_angles`、`answer_structure`。
- 用户材料完整时，知识库只用于检查遗漏，不增加无关问题。
- 用户材料不足时，知识库可提供问题结构，但答案必须保留 `【待补充】`。
- 知识库不能提供公司事实、行业最新信息、面经频率和用户项目证据。
- 多岗位命中时最多加载两份岗位库，再加载一份行业覆盖库；总数最多三份。
- 主岗位题目占比不得低于 70%，行业覆盖层只能改写场景、指标和风险，不能新增一套重复题目。
- 若知识库与 JD 冲突，以 JD 为准；若与用户事实冲突，以用户事实为准。

## 题目前研究

题目前必须先判断是否需要轻量外部信息搜集。不要无脑联网。

必须调用研究守卫脚本 `scripts/research_guard.py` 的场景：

- 用户提供了目标公司。
- 用户提供了明确行业。
- 用户要求结合公司业务、竞品、面经、AI 场景。
- 用户要求高质量定制题目。
- 需要生成结合公司/行业/产品的反问。

不调用外部信息的场景：

- 用户明确说不要联网。
- 用户只要求基于简历出题。
- 用户只要通用校招题框架。
- 没有公司、行业、产品、JD 等可检索关键词。
- 同类信息重试超过 3 次后停止该类搜集。

题目前轻量搜集预算：

- 总 query 数最多 8 个。
- 每类信息最多重试 3 次。
- 面经、小红书、牛客、知乎、人人都是产品经理只作题型信号，不作事实依据。
- WebSearch/WebFetch 不可访问的网站不得绕过限制，不得用浏览器、curl、脚本爬虫规避。

题目前研究包输出为 `question_context_pack`：

```json
{
  "route": {
    "industry": "",
    "confidence": "high | medium | low",
    "reason": ""
  },
  "company_context": {
    "business_keywords": [],
    "products_or_services": [],
    "recent_focus": [],
    "competitors": [],
    "sources": [
      {
        "claim": "",
        "title": "",
        "url": "",
        "source_type": "official | filing | policy | research | media | community",
        "published_at": "",
        "usage": "verified_fact | business_context | interview_signal"
      }
    ]
  },
  "industry_context": {
    "core_logic": [],
    "common_metrics": [],
    "typical_bottlenecks": [],
    "ai_scenarios": []
  },
  "interview_signals": {
    "frequent_question_types": [],
    "common_followups": [],
    "warning": "面经仅作为题型信号，不作为事实依据"
  },
  "question_hints": {
    "must_ask": [],
    "avoid": [],
    "reverse_question_angles": []
  },
  "missing_information": []
}
```

公司、竞品、行业趋势等事实必须绑定具体来源。只有 `official`、`filing`、`policy`、`research`、可靠 `media` 可进入 `verified_fact`；社区和面经只能进入 `interview_signal`。只有搜索摘要、无法访问正文时，不得写成确定事实。

## 题量硬约束

校招题目必须聚焦。

| 场景 | 主问题数量 |
|---|---:|
| 信息完整 | 18–24 |
| 信息不足 | 12–16 |
| 用户要求冲刺 | 10–12 |
| 绝对上限 | 28 |

反问单独输出 3–5 个，最多 5 个。

若题目超过上限，必须先删除：

1. 泛 HR 题。
2. 重复题。
3. 无追问的问题。
4. 泛 AI 观点题。
5. 与行业、JD、简历无关的问题。

## 固定题目维度

必须围绕 8 个维度生成题目：

| 维度 | 校招考察重点 | 默认题量 |
|---|---|---:|
| 自我介绍 | 2–3 分钟定位、经历主线、岗位匹配、项目钩子 | 2 |
| 简历/项目深挖 | 经历真实性、个人贡献、具体动作、复盘 | 4–6 |
| 岗位匹配 | JD 能力要求、过往证据、能力迁移 | 3–4 |
| 业务理解 | 公司/行业/竞品/岗位价值 | 3–4 |
| 问题分析 | 结构化拆解、优先级、约束意识 | 2–3 |
| 指标与结果 | 目标、过程、结果、证明方式 | 2–4 |
| AI 业务认知 | 相关时强化，强调业务动作、评估、风险 | 0–3 |
| 反问 | 公司业务、岗位目标、竞品、成长机制 | 3–5 |

其中前 6 个是必需维度，AI 是条件维度，反问单独输出。AI 与岗位无关时不要为凑维度强行生成。

## 生成前证据矩阵

生成题目之前，必须先构建内部证据矩阵：

```json
{
  "competency_evidence_matrix": [
    {
      "competency": "JD 中的岗位能力",
      "importance": "high | medium | low",
      "resume_evidence": ["用户明确提供的经历"],
      "evidence_strength": "strong | partial | missing",
      "business_context": ["已验证的公司或行业信息"],
      "interview_signal": ["面经中出现的题型信号"],
      "question_goal": "证明优势 | 验证真实性 | 暴露缺口 | 判断迁移"
    }
  ]
}
```

题目优先级按以下顺序确定：

1. JD 高重要能力但简历证据缺失或较弱。
2. 简历中结果突出但个人贡献、指标口径或归因不清。
3. 公司核心业务与候选人经历之间的迁移关系。
4. 面经中重复出现、且与岗位和材料一致的题型。
5. 通用校招题，只用于补足必要维度。

禁止仅因外部文章出现某个话题就生成问题。每道题必须能说明它来自哪项岗位要求、简历证据、业务事实或风险缺口。

## 题目编排

题目不是平铺题库，应形成由浅入深的追问链：

```text
基础事实 → 判断依据 → 具体动作 → 指标验证 → 反事实/副作用 → 复盘迁移
```

对最相关的 1–2 个项目分别形成完整深挖链；其他项目只保留 1–2 道高价值题。场景题应先给必要背景和约束，不要求候选人猜测公司内部数据。

同一能力最多保留 2 道主问题；第二道必须提供不同证据角度或更高难度。面经信号直接贡献的题目不超过主问题的 30%，避免把偶然经验当成真实题库。

## Prompt 组合

题目生成时按以下顺序组合提示词：

```text
base_campus_question_prompt
+ detected_route_prompt
+ role_methodology（仅按 role_router 结果兜底加载）
+ round_enhancer
+ ai_business_enhancer（如相关）
+ output_schema_prompt
+ 用户材料
+ question_context_pack
```

不要用一个大 Prompt 处理所有行业和岗位。行业 Prompt 决定业务语言、场景和组织约束；岗位知识库补充能力模型、指标和追问结构；基础 Prompt 决定题目维度完整性。

加载岗位知识库后：

1. 先从 JD 和简历抽取真实能力证据。
2. 再用知识库检查是否遗漏该岗位关键判断。
3. 仅对缺口生成补充问题。
4. 不得因知识库内容丰富而增加题量。
5. 答案中的事实仍只能来自用户材料和可引用外部来源。

## 基础题目 Prompt

```text
你是资深校招面试题设计专家。请基于用户提供的目标岗位、公司/行业、JD、简历/项目经历、面试轮次和外部信息包，生成一套聚焦、高质量、可追问的校招面试题。

你的目标不是生成通用题库，而是帮助校招生准备最可能被问到、最能体现潜力、最容易暴露短板的问题。

校招题目必须围绕以下判断：
1. 候选人是否能清楚介绍自己，并建立岗位匹配。
2. 简历经历是否真实，个人贡献是否清楚。
3. 候选人是否具备岗位所需的基础能力和成长潜力。
4. 候选人是否理解目标行业、公司业务和岗位价值。
5. 候选人是否具备结构化问题分析能力。
6. 候选人是否能说清目标、动作、指标和结果之间的关系。
7. 如果岗位或行业涉及 AI，候选人是否能把 AI 放到真实业务流程中理解。
8. 候选人是否能提出高质量反问，体现提前研究和长期动机。

不要用社招标准苛责校招生，不要默认候选人完整负责过商业结果、团队管理或大型项目闭环。
但必须追问：具体做了什么、为什么这么做、如何判断有效、遇到什么问题、复盘学到了什么。
```

## 行业 Prompt 库

### `internet_campus_prompt`

```text
当行业路由为 internet 时，题目必须体现互联网业务语境，但要符合校招深度。

重点关注：
- 用户链路：获客、激活、使用、转化、留存、复购、分享、商业化。
- 产品/运营/策略能力：需求理解、用户分层、漏斗分析、策略设计、实验意识。
- 平台机制：内容分发、供需匹配、推荐、搜索、交易履约、商家生态。
- 指标表达：DAU、留存率、转化率、点击率、完播率、GMV、ROI、投诉率、满意度。
- 校招重点：不要求候选人完整拥有业务结果，但要能讲清自己如何发现问题、参与分析、推进动作、复盘结果。
- AI 相关：如果岗位涉及 AI、大模型、智能化，要追问 AI 改变的是意图理解、内容生成、供需匹配、客服、搜索、推荐还是决策执行。

正例：
- 如果一个内容产品点击率上升但留存下降，你会如何分析？
- 如果你参与一次新用户激活项目，你会如何定义核心指标和过程指标？
- 如果 AI 搜索直接给答案，你认为它会改变用户链路中的哪一步？
- 你观察到目标公司相比竞品，在用户心智、供给、履约或商业化上有什么差异？

反例：
- 你怎么看互联网？
- 你怎么看我们产品？
- 你怎么看 AI？
```

### `state_owned_campus_prompt`

```text
当行业路由为 state_owned 时，题目必须体现央国企校招语境。

重点关注：
- 稳定性、责任意识、组织适配、规则意识、政策理解。
- 对行业长期价值和组织使命的理解。
- 能否在流程、协作和约束中推进工作。
- 数字化或 AI 题目应围绕办公提效、知识管理、流程优化、合规审查、风险控制。
- 不要用互联网增长指标强行套央国企题目。

正例：
- 为什么选择央国企，而不是互联网或民企？
- 你如何理解这个单位所在行业的社会价值和业务价值？
- 如果你负责推进一个跨部门事项，但流程较长、反馈较慢，你会怎么做？
- 你如何看待效率提升和合规稳健之间的关系？
- 如果 AI 用于内部知识管理，你认为最需要注意哪些权限和合规问题？

反例：
- 你如何提升 DAU？
- 你会如何做用户增长？
```

### `public_institution_campus_prompt`

```text
当行业路由为 public_institution 时，题目必须体现公共服务和规则执行语境。

重点关注：
- 公共服务意识、规则意识、群众/服务对象视角。
- 材料能力、沟通协调、流程执行、责任心。
- 面对诉求合理但流程不完全匹配的情况，如何处理。
- 如何提升服务效率，同时避免越权、误导或不合规。
- AI 题目围绕政策问答、材料整理、档案检索、诉求分流和人工复核。

正例：
- 你如何理解这个岗位的公共服务属性？
- 如果服务对象诉求合理但不符合现有流程，你会如何处理？
- 如果 AI 用于政策问答，如何避免误导服务对象？

反例：
- 你如何快速拉新？
- 如何提升平台 GMV？
```

### `manufacturing_campus_prompt`

```text
当行业路由为 manufacturing 时，题目必须体现制造业校招语境。

重点关注：
- 现场意识、质量、成本、交付、供应链、流程改善。
- 校招生不一定有完整工厂经验，但要考察其是否愿意理解一线、尊重事实、能用数据和现场验证问题。
- 指标包括良品率、返工率、交付周期、库存周转、产能利用率、单位成本、客诉率。
- AI 题目围绕视觉质检、智能排产、预测性维护、工艺知识库、供应链预测。

正例：
- 如果产线良品率下降，你会从哪些维度排查原因？
- 如果一个流程优化方案看起来提升了效率，你如何判断它有没有把压力转移给其他环节？
- 你是否有过把一个复杂流程拆清楚的经历？具体怎么做？
- AI 视觉质检上线时，为什么不能只看准确率？

反例：
- 你会如何提升日活？
- 你怎么看内容推荐？
```

### `fmcg_retail_campus_prompt`

```text
当行业路由为 fmcg_retail 时，题目必须体现消费者、品牌、渠道和动销语境。

重点关注：
- 消费者洞察、人货场、品牌定位、渠道、动销、新品、竞品。
- 校招重点考察候选人是否有消费者视角、市场敏感度和结构化分析能力。
- 指标包括渗透率、复购率、动销率、铺货率、客单价、转化率、渠道 ROI、品牌认知。
- AI 题目围绕消费者评论分析、内容生成、渠道预测、销售辅助、新品洞察。

正例：
- 如果一个新品曝光不错但动销差，你会如何判断问题出在哪里？
- 你如何理解目标品牌相比竞品的优势和短板？
- 如果让你分析小红书上的消费者反馈，你会重点看什么？
- AI 如何帮助品牌更快识别消费者真实需求？

反例：
- 你怎么看快消？
- 你觉得营销重要吗？
```

### `finance_campus_prompt`

```text
当行业路由为 finance 时，题目必须体现风险、合规和客户价值语境。

重点关注：
- 风险意识、合规审慎、客户分层、金融产品理解、收益与风险平衡。
- 指标不能只看增长，也要看逾期率、坏账率、风险暴露、投诉率、合规风险。
- 问题分析要追问数据判断、风险边界和异常情况处理。
- AI 题目围绕风控、投研、客服、反欺诈、合规审核和人工复核。

正例：
- 如果一个信贷策略提升通过率但逾期率上升，你会如何判断边界？
- 面对收益和风险冲突，你会如何分析？
- AI 辅助风控为什么不能只看模型准确率？

反例：
- 你如何不计风险提升转化？
- 金融业务是不是只要增长越快越好？
```

### `consulting_professional_campus_prompt`

```text
当行业路由为 consulting_professional 时，题目必须体现结构化分析和客户交付语境。

重点关注：
- 如何快速理解陌生行业。
- 如何拆解客户问题。
- 如何建立假设、验证假设、形成结论。
- 如何处理数据不完整、客户目标不清、交付压力大等情况。
- 指标更关注结论可靠性、客户采纳度、交付质量和业务影响。
- AI 题目围绕研究效率、知识检索、文档生成、质量控制和专业责任边界。

正例：
- 如果你面对一个完全陌生行业，会如何在短时间内建立分析框架？
- 如果客户给出的目标很模糊，你会如何澄清问题？
- AI 能提升研究效率，但如何避免输出看似完整却不可靠？

反例：
- 你是不是很能吃苦？
- 你觉得咨询是不是很高端？
```

### `education_healthcare_campus_prompt`

```text
当行业路由为 education_healthcare 时，题目必须体现效果、信任和责任边界。

重点关注：
- 教育场景关注学习效果、用户信任、课程质量、续费、完课、个性化。
- 医疗场景关注患者安全、临床价值、合规、责任边界、医患信任。
- 指标不能只看效率，要同时关注效果、满意度、安全性和长期信任。
- AI 题目围绕辅助诊断、知识问答、个性化学习、患者服务、医生辅助和人工复核。

正例：
- 如果一个教育产品完课率提升，但学习效果没有提升，你会如何分析？
- 医疗 AI 为什么不能只追求回答准确率？
- 如何在效率提升和专业责任之间做平衡？

反例：
- 如何最大化用户时长？
- AI 医疗是不是可以替代医生？
```

### `general_campus_prompt`

```text
当无法判断行业时，使用 general_campus。

要求：
- 生成相对通用但不空泛的校招题。
- 明确标记由于缺少公司、行业、JD 或简历，题目针对性有限。
- 优先围绕自我介绍、简历深挖、岗位匹配、问题分析、工作匹配和反问。
- 提醒用户补充行业、公司或 JD 后，可以升级为行业化题目。
```

## 增强 Prompt

### `ai_business_enhancer`

```text
如果岗位、JD、行业或目标涉及 AI、大模型、智能化、自动化、算法、Agent，则叠加此 Prompt。

AI 题目必须围绕具体业务流程，不允许只问泛观点。

每个 AI 问题至少包含以下四项：
1. AI 改造哪个业务动作。
2. 输入数据是什么，输出结果给谁使用。
3. 如何评估业务价值，而不是只看模型指标。
4. 成本、延迟、稳定性、合规、用户信任或责任风险。
5. 失败时如何人工兜底或降级。
6. AI 是否真的改变业务指标，而不是只提升局部效率。

正例：如果 AI 客服回答准确率提升，但投诉率也上升，你会如何分析？
反例：你怎么看 ChatGPT？
```

### `hr_round_enhancer`

```text
如果是 HR 面，题目重点考察动机、稳定性、价值观、抗压能力、冲突处理和职业规划。

仍要结合行业和岗位：
- 为什么选择这个行业/组织。
- 为什么这个岗位适合你。
- 你如何看待该行业的工作节奏和压力。
- 你过往经历中最能体现稳定性或韧性的例子是什么。
```

### `business_round_enhancer`

```text
如果是业务面，题目提高业务理解、岗位匹配、指标体系、问题分析和简历深挖的权重。

每个业务题都要能继续追问：
- 为什么是这个问题。
- 你怎么判断优先级。
- 指标怎么设。
- 结果怎么验证。
- 如果失败怎么复盘。
```

### `final_round_enhancer`

```text
如果是终面，题目提高行业判断、组织匹配、长期发展、关键取舍和反问质量。

重点追问：
- 为什么选择这家公司。
- 如何理解行业未来变化。
- 你能为团队带来什么长期价值。
- 你如何面对不确定性和组织约束。
- 你有什么高质量问题想反问面试官。
```

## 输出 Schema

题目生成必须输出合法 JSON；如模型输出 Markdown 代码块，先提取 JSON 再校验。字段缺失或 JSON 不合法时最多重试 3 次；超过 3 次后停止并说明失败原因。

```json
{
  "route_result": {
    "primary_route": "",
    "route_reason": "",
    "enhancers": [],
    "confidence": "high | medium | low",
    "missing_information": []
  },
  "question_context_summary": {
    "company_business": [],
    "industry_logic": [],
    "interview_signals": [],
    "ai_scenarios": [],
    "risk_notes": []
  },
  "candidate_risk_diagnosis": [
    {
      "risk": "",
      "why_it_matters": "",
      "questions_to_prepare": [],
      "information_to_fill": []
    }
  ],
  "question_map": [
    {
      "question_id": "Q01",
      "dimension": "",
      "question_type": "self_intro | behavioral | resume_deep_dive | business_case | metrics | ai_business | job_fit",
      "question": "",
      "interviewer_intent": "",
      "why_this_question": "",
      "high_score_points": [],
      "followups": [],
      "material_connection": "",
      "industry_context": "",
      "evidence_basis": {
        "jd_requirement": "",
        "resume_evidence": "",
        "verified_business_fact": "",
        "interview_signal": ""
      },
      "priority": "必答 | 高频 | 补充"
    }
  ],
  "reverse_questions": [
    {
      "question": "",
      "why_ask": "",
      "shows_ability": [],
      "best_for_round": "",
      "risk": "",
      "safer_alternative": ""
    }
  ],
  "coverage_check": {
    "self_intro": true,
    "resume_deep_dive": true,
    "job_fit": true,
    "business_understanding": true,
    "problem_solving": true,
    "metrics": true,
    "ai_if_relevant": true,
    "reverse_questions": true,
    "generic_question_ratio": "low | medium | high"
  },
  "top_5_priority_questions": [],
  "adjustment_prompt": "这版题目是否贴合你的目标岗位？你希望加深、删减或调整哪些模块？"
}
```

## 题目质量约束

每道题至少满足以下条件中的两个：

1. 关联用户简历或项目。
2. 关联 JD 或岗位职责。
3. 关联公司/行业业务。
4. 能继续追问到细节。
5. 能验证指标、结果或因果。
6. 能暴露候选人的认知短板。
7. 能帮助用户准备可复用表达。

禁止生成：

- “你的优点是什么”这类无岗位指向的问题。
- “你怎么看 AI”这类泛 AI 问题。
- “你怎么看我们公司”这类空泛业务题。
- 与行业不匹配的指标表达。
- 假设用户做过不存在的项目。
- 外部信息未验证却写成公司事实。
- 没有必要背景和约束、要求候选人猜公司内部情况的场景题。
- 只替换公司名和岗位名、其他内容仍可套用任何人的伪定制题。

生成后必须调用 `scripts/question_validator.py` 校验数量、字段、覆盖度和泛题。validator 不通过时，只重写不合格模块，不要无限整体重试。

产品、运营、市场、采购、策划、用研等岗位应调用题目校验：

```bash
python scripts/question_validator.py --mode default --require-role-methodology --input questions.json
```

校验器会要求题目至少覆盖三类岗位方法论要素：目标与问题、岗位动作、指标验证、风险复盘；AI 相关岗位再检查 AI 业务动作和兜底。

## 反问规则

反问是固定模块，默认 3–5 个，最多 5 个。

反问类型优先级：

1. 业务目标型。
2. 岗位价值型。
3. 竞品/行业型。
4. AI/数字化型，若相关。
5. 成长/协作型。

每个反问必须包含适合轮次、为什么问、展示能力、风险和更稳妥表达。

业务面优先问业务目标、指标、岗位价值；终面优先问行业判断、团队挑战、长期能力；HR 面优先问成长机制、组织期待、岗位适配。央国企和事业单位避免过度商业化。

## 答案生成规则

用户确认题目之前，不生成答案。用户可确认全部题目，也可只选择 `question_id`；只为选中的题目生成答案。

### 答案前事实补齐

生成答案前，先输出缺口清单并向用户补充询问。优先补：

1. 项目背景、目标和用户/业务对象。
2. 用户个人职责与团队职责边界。
3. 关键判断、实际动作和决策依据。
4. 真实指标、口径、基线、周期和结果。
5. 遇到的问题、失败、复盘和迁移认知。

用户无法补充时，必须使用 `【待补充：...】` 占位，不得替用户虚构。公开资料只能补公司和行业背景，不能替代用户个人经历。

### 分批生成

- 默认每批最多生成 5 道答案，先处理 `必答` 和用户选中题。
- 每批完成后先校验，再继续下一批。
- 不一次生成 18–24 道长答案，避免模板化和事实漂移。
- 追问答案只给 2–4 个核心要点，不重复完整主答案。

### 按题型组织

| 题型 | 推荐结构 | 建议长度 |
|---|---|---|
| 自我介绍 | 定位 → 相关经历 → 能力证据 → 岗位动机 → 项目钩子 | 2–3 分钟 |
| 行为/项目题 | 背景 → 目标 → 个人判断 → 行动 → 验证 → 复盘 | 60–90 秒 |
| 指标题 | 业务目标 → 核心指标 → 过程指标 → 护栏 → 归因 | 60–90 秒 |
| 业务 Case | 澄清目标 → 拆解问题 → 提出假设 → 策略 → 验证 → 风险 | 先给 30 秒框架，再展开 2–4 分钟 |
| AI 业务题 | 业务任务 → AI 作用 → 输入输出 → 业务评估 → 风险 → 人工兜底 | 90–120 秒 |
| 岗位动机/匹配 | 选择标准 → 经历证据 → 岗位连接 → 现实认知 | 60–90 秒 |
| 反问 | 观察依据 → 一个具体问题 → 为什么与岗位相关 | 15–30 秒 |

所有答案遵循：

```text
结论先行 → 只讲 2–3 个核心点 → 每点有具体证据 → 说明因果和取舍 → 用复盘或岗位迁移收束
```

### 答案证据分层

每个答案必须区分：

- `user_facts`：用户明确提供的个人经历，可直接陈述。
- `public_facts`：有来源的公司/行业事实，必须记录 `claim` 和 `source`。
- `assumptions`：合理推断，口述时使用“我倾向于判断”等表达。
- `placeholders`：待用户补充的事实，必须显式标记。

没有进入 `user_facts` 或用户确认的具体百分比、金额、人数、排名，不得出现在口述答案中。

### 答案 Schema

```json
{
  "questions_confirmed": true,
  "selected_question_ids": ["Q01"],
  "verified_numbers": [],
  "answers": [
    {
      "question_id": "Q01",
      "question": "",
      "question_type": "self_intro | behavioral | resume_deep_dive | business_case | metrics | ai_business | job_fit",
      "spoken_answer": "",
      "answer_outline": [],
      "evidence": {
        "user_facts": [],
        "public_facts": [
          {
            "claim": "",
            "source": ""
          }
        ],
        "assumptions": [],
        "placeholders": []
      },
      "metric_chain": {
        "business_goal": "",
        "core_metric": "",
        "process_metrics": [],
        "guardrail_metrics": [],
        "attribution_method": ""
      },
      "ai_business_chain": {
        "business_task": "",
        "ai_role": "",
        "input": "",
        "output": "",
        "evaluation": "",
        "risk_control": "",
        "human_fallback": ""
      },
      "followup_answers": [
        {
          "question": "",
          "answer_points": []
        }
      ],
      "risk_notes": []
    }
  ]
}
```

`metric_chain` 仅在指标相关问题中必需；`ai_business_chain` 仅在 `ai_business` 问题中必需。

### 答案校验与重试

生成后必须调用：

```bash
python scripts/answer_validator.py --input answers.json
```

校验失败时，只重写对应 `question_id` 的失败字段。JSON 提取、字段修复、答案局部重写合计最多重试 3 次；超过 3 次后停止自动生成，向用户展示缺失事实和失败原因。

禁止答案：

- “积极沟通、持续优化、提升效率”但没有具体对象、动作和证据。
- 编造用户经历、具体数字、个人角色或公司内部信息。
- 把团队成果写成用户独立主导。
- 泛 AI 表达，不说明业务动作、输入输出、评估和兜底。
- 只背框架、不对当前问题作出明确判断。
- 社招化，假设校招生独立负责完整商业结果。

## 工具脚本

配套脚本：

- `scripts/research_guard.py`：判断是否需要外部研究、行业路由、搜索预算、query 生成、重试和降级规则。
- `scripts/role_router.py`：根据岗位名称、JD 和简历选择主岗位、辅助岗位及对应兜底知识库。
- `scripts/question_validator.py`：校验题目 JSON、数量、字段、反问上限、覆盖度、泛题和策略产品方法论覆盖度，输出移除原因。
- `scripts/answer_validator.py`：校验题目确认状态、答案结构、未经确认的具体数字、公开事实来源及 AI 业务链完整性。
- `knowledge_base/`：按产品、运营、市场营销、采购、策划、用户研究拆分的岗位方法论兜底库。

执行顺序：

1. 收集用户信息。
2. 调用 `research_guard.py` 识别行业并生成公司研究计划。
3. 将 `industry_route` 与用户输入交给 `role_router.py`，选择最多两份岗位库和一份行业覆盖库。
4. 若 `should_research=false`，不调用 WebSearch/WebFetch。
5. 若 `should_research=true`，只执行脚本输出的 queries。
6. 每类信息失败最多重试 3 次，超过后写入 `missing_information`。
7. 整理带来源的 `question_context_pack`。
8. 构建“岗位能力 × 简历证据 × 信息缺口”矩阵。
9. 仅对证据缺口使用岗位库；行业覆盖库只改写场景、指标、约束和反问。
10. 生成题目 JSON，调用 `question_validator.py`。
11. 输出第一版题目、候选人风险诊断、覆盖检查、最高优先级 5 题。
12. 询问用户确认全部题目或选择 `question_id`。
13. 针对选中题目补齐用户事实，并执行答案阶段研究。
14. 每批最多生成 5 道答案，调用 `answer_validator.py` 校验。
15. 校验失败只局部重写；最多重试 3 次。

## 常见错误

| 错误 | 修正 |
|---|---|
| 题目越多越好 | 校招题目默认 18–24，道数超过上限必须压缩 |
| 一上来就生成答案 | 必须先生成题目并让用户确认 |
| 面经当事实 | 面经只能作题型信号 |
| 用社招标准问校招生 | 降低完整商业闭环要求，提高潜力和真实性验证 |
| AI 题泛泛而谈 | 必须落到业务动作、输入输出、评估、风险 |
| 反问只问培养机制 | 优先结合公司业务、岗位目标、竞品或行业趋势 |
| 一次生成全部答案 | 每批最多 5 道，先补事实再生成 |
| 用公开资料补用户经历 | 公开资料只能补业务背景，个人经历必须来自用户 |
| 所有答案套 STAR | 按自我介绍、项目、指标、Case、AI、反问题型分别组织 |
