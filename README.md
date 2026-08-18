# 文科生求职

面向文科、商科和非技术类校招岗位的面试准备插件。它根据目标岗位、公司/行业、JD、简历项目和面试轮次生成问题、追问、风险诊断、反问和结构化答案。

## 支持岗位

- 产品：产品经理、策略产品、AI 产品、产品策划。
- 运营：用户、内容、活动、社群、新媒体、商家和增长运营。
- 市场营销：品牌、市场推广、整合营销、内容营销、公关。
- 采购：寻源、供应商管理、招采、成本和供应链采购。
- 策划：活动、内容、品牌、宣传、文案和项目策划。
- 用户研究：用研、消费者研究、市场研究、访谈、问卷和可用性测试。
- 销售商务：销售、商务拓展、渠道、大客户和解决方案销售。
- 人力资源：招聘、培训、组织发展、员工关系和 HRBP。
- 行政宣传：行政、新闻宣传、企业文化、材料、公文和舆情。
- 客户成功与项目交付：实施、上线、客户采用、项目管理、续约和扩容。
- 其他文科类岗位：依据 JD、简历和行业信息直接生成，不强行套知识库。

## 核心逻辑

```text
用户材料
→ 行业路由：决定业务语境
→ 岗位路由：选择最多两份岗位方法论
→ 行业覆盖：选择一份行业语境库
→ JD × 简历证据矩阵
→ 外部研究：补公司、行业和面经信号
→ 生成并校验题目
→ 用户确认
→ 分批生成并校验答案
```

岗位知识库和行业覆盖库都只是兜底，不得覆盖用户事实。用户材料完整时，知识库只检查遗漏；材料不足时，知识库提供问题和答案结构，但所有个人事实必须使用 `【待补充】`。最多加载两份岗位库和一份行业覆盖库。

## 目录

```text
liberal-arts-job-interview-plugin/
├── .trae-plugin/plugin.json
├── skills/liberal-arts-job-interview/
│   ├── SKILL.md
│   ├── knowledge_base/
│   │   ├── product_methodology.md
│   │   ├── operations_methodology.md
│   │   ├── marketing_methodology.md
│   │   ├── procurement_methodology.md
│   │   ├── planning_methodology.md
│   │   ├── user_research_methodology.md
│   │   ├── sales_bd_methodology.md
│   │   ├── human_resources_methodology.md
│   │   ├── administration_publicity_methodology.md
│   │   ├── customer_success_project_methodology.md
│   │   └── industry_*.md
│   ├── scripts/
│   │   ├── role_router.py
│   │   ├── research_guard.py
│   │   ├── question_validator.py
│   │   └── answer_validator.py
│   └── tests/
├── examples/
├── CHANGELOG.md
├── LICENSE
└── VERSION
```

## 使用输入

```text
目标岗位：市场营销策划
目标公司/行业：某快消品牌
JD：负责消费者洞察、品牌传播和营销活动复盘
面试轮次：业务一面
简历项目：提供真实职责、动作、指标和复盘
强化方向：项目深挖、市场分析、指标、反问
```

## 脚本

岗位与知识库路由：

```bash
python skills/liberal-arts-job-interview/scripts/role_router.py \
  --input examples/meituan-strategy-product-input.json
```

公司与行业研究计划：

```bash
python skills/liberal-arts-job-interview/scripts/research_guard.py \
  --input examples/meituan-strategy-product-input.json
```

题目校验：

```bash
python skills/liberal-arts-job-interview/scripts/question_validator.py \
  --mode default \
  --require-role-methodology \
  --input examples/meituan-strategy-product-questions.json
```

答案校验：

```bash
python skills/liberal-arts-job-interview/scripts/answer_validator.py \
  --input examples/meituan-strategy-product-answers.json
```

## 约束

- 面经和社区信息只作题型信号。
- 公司与行业事实必须有公开来源。
- 知识库不能替代用户经历或公司研究。
- 最多加载主岗位、一个辅助岗位知识库和一份行业覆盖库。
- 用户确认题目后才生成答案。
- 答案每批最多 5 道，未经确认的数字不得写入口述稿。
