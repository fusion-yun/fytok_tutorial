---
myst:
  substitutions:
    FyTok: _Fy_<font color="blue" />__Tok__
    SpDM: _Sp_<font color="blue" />__DM__
---

## 关于本文档

{{SpDM}} 是一个 Python 库，主要包含数据集成、建模和可视化工具。{{SpDM}} 为 {{FyTok}} 提供了物理语义无关的核心功能和基础架构。对于希望添加数据源或物理程序的用户，建议阅读本文档的第二部分 “SpDM (SpDB) 数据集成建模”，了解数据和程序接口，以及辅助工具。



## 名词表

```{glossary}

CRAFT
  Comprehensive Research Facility for Fusion Technology，聚变堆主机关键系统综合研究设施项目

DD
  Data Dictionary (数据字典)，本文特指IMAS的数据字典，作为托卡马克数据标准规范。

HTree
  Hierarchical tree，分层树状结构，是一种数据结构，用于存储层次化的数据。

IDS
  Interface Data structure, IMAS DD 数据结构中最大的组成单位，对应一个相对独立的物理概念或者装置组件。

IM
  Integrated Modeling

IMAS
  Integrated Modelling & Analysis Suite， ITER组织开发的集成建模与分析软件套件

ITER
  International Thermonuclear Experimental Reactor

Ontology
  本体，是（特定领域）信息组织的一种形式，是领域知识规范的抽象和描述，是表达、共享、重用知识的方法

URI
  Uniform Resource Identifier
```

## 获得本文档

  可以通过以下方式获得本文档：

  - git@gitee.com:fusion_yun/fytok_tutorial.git
  - 

## 本文档的组织结构

```{tableofcontents}

```

## 版本信息

- 版本：alpha
- 日期：2023-11-28

## 开发人员

- 于治, Zhi Yu, yuzhi@ipp.ac.cn (ASIPP)
- 刘晓娟, Xiaojuan Liu, lxj@ipp.ac.cn (ASIPP)
- ......

## 致谢

本工作得到了如下项目的支持

- 国家磁约束核聚变能发展研究专项（National MCF Energy R&D Program under Contract），氘氚聚变等离子体中 alpha 粒子过程对等离子体约束 性能影响的理论模拟研究，Alpha 粒子密度和能谱分布的集成建模研究，编号 2018YFE0304102
- 《聚变堆主机关键系统综合研究设施（CRAFT，Comprehensive Research Facility for Fusion Technology Program of China））》项目《总控课题： 集成数值建模和数据分析系统框架开发》，（项目编号：2018-000052-73-01-001228.）