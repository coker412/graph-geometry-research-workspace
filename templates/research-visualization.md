# 研究路线与证明依赖可视化模板

将下面两个部分分别复制为项目中的 `research-tree.md` 和 `proof-map.md`。

## research-tree.md：探索过程

### 当前状态

- 主问题：
- 当前主路线：
- 最新关键事件：
- 最大障碍：
- 下一步：

### 路线图

```mermaid
flowchart TD
    P0["P0 主问题<br/>exploring"]
    A1["A1 直接计算<br/>pushing"]
    A2["A2 谱方法<br/>blocked"]
    E1["E1 小规模实验<br/>experimental"]
    C1["C1 反例"]
    S11["S1.1 关键引理<br/>proof-draft"]
    V1["V1 verifier<br/>wrong: gap"]

    P0 -->|decomposes-to| A1
    P0 -->|decomposes-to| A2
    E1 -.->|supports only| A1
    C1 -->|refutes| A2
    A1 -->|depends-on| S11
    S11 -->|verified-by| V1

    classDef active fill:#fff2a8,stroke:#8a6d00,color:#111;
    classDef blocked fill:#ffd6d6,stroke:#a40000,color:#111;
    classDef partial fill:#d8eaff,stroke:#1d5fa7,color:#111;
    classDef verified fill:#d9f2d9,stroke:#267326,color:#111;
    classDef evidence fill:#eeeeee,stroke:#666,color:#111;

    class P0,A1 active;
    class A2,C1,V1 blocked;
    class S11 partial;
    class E1 evidence;
```

### 分支卡片

#### A1 — 路线名称

- 状态：`pushing`
- 核心直觉：
- 有序子目标：
- 支持证据：
- 当前障碍：
- 对应日志：
- 下一步：

#### A2 — 路线名称

- 状态：`blocked`
- 失败位置：
- 失败类型：
- 反例或证据：
- 可复用观察：

---

## proof-map.md：候选证明依赖

### 当前状态

- 目标定理：
- 当前证据等级：
- 当前最小缺口：
- 候选证明文件：
- 最近一次验证报告：

### 依赖图

```mermaid
flowchart BT
    D1["D1 定义与归一化<br/>internal · human-verified"]
    L1["L1 外部定理<br/>literature · theorem-checked"]
    P1["P1 局部公式<br/>internal · agent-verified"]
    P2["P2 单调性引理<br/>internal · proof-draft<br/>GAP: 边界情形"]
    T0["T0 主定理<br/>internal · proof-draft"]
    E1["E1 n≤8 实验<br/>experimental"]

    D1 --> P1
    L1 --> P1
    D1 --> P2
    P1 --> T0
    P2 --> T0
    E1 -.->|supports only| P2

    classDef verified fill:#d9f2d9,stroke:#267326,color:#111;
    classDef draft fill:#d8eaff,stroke:#1d5fa7,color:#111;
    classDef gap fill:#ffd6d6,stroke:#a40000,color:#111;
    classDef experimental fill:#eeeeee,stroke:#666,color:#111;

    class D1,L1,P1 verified;
    class T0 draft;
    class P2 gap;
    class E1 experimental;
```

### 节点登记表

| ID | 命题 | 来源 | 证据等级 | 证明/来源文件 | 验证状态 | 下游影响 |
|---|---|---|---|---|---|---|
| D1 | 定义与归一化 | internal | human-verified | `README.md` | closed | P1, P2 |
| L1 | 外部定理 | literature | theorem-checked | `references.md#L1` | closed | P1 |
| P1 | 局部公式 | internal | agent-verified | `notes/local-formula.md` | closed | T0 |
| P2 | 单调性引理 | internal | proof-draft | `notes/monotonicity.md` | gap | T0 |
| T0 | 主定理 | internal | proof-draft | `notes/main-proof.md` | blocked by P2 | — |

### 未关闭缺口

#### GAP-P2-1

- 位置：
- 所需结论：
- 已尝试路线：
- 反例测试：
- 影响节点：
- 下一步：
