# Proof Map

```mermaid
flowchart TD
    P0["P0: |E|=|V|-1<br/>proof-draft"]
    A1["A1: 对 |V| 归纳<br/>proof-draft"]
    S1["S1: 有限非平凡树存在叶子<br/>proof-draft"]
    S2["S2: 删除叶子后仍为树<br/>proof-draft"]

    P0 -->|depends-on| A1
    A1 -->|depends-on| S1
    A1 -->|depends-on| S2
```

| Node | 命题 | 来源 | 证据等级 | 证据 | 当前 gap |
|---|---|---|---|---|---|
| P0 | 有限非空树满足 \(|E|=|V|-1\) | internal-offline | proof-draft | `notes/proof.md` | 缺少独立审查 |
| A1 | 删叶归纳覆盖所有 \(|V|\ge 1\) | internal-offline | proof-draft | `notes/proof.md` | 缺少独立审查 |
| S1 | \(|V|\ge 2\) 时存在度为 1 的顶点 | internal-offline | proof-draft | `notes/proof.md` | 缺少独立审查 |
| S2 | 删除叶子及其关联边后仍为树 | internal-offline | proof-draft | `notes/proof.md` | 缺少独立审查 |
