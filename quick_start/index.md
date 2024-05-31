FyTok 快速启动
=======================

## 1. 安装
- 软件环境
- 安装
- 开发环境（本地配置）： vscode，jupyter
- 源码， issue 

## 2. case 1: 数据集成： 平衡分析
- 装置描述 （Device）
- 平衡文件
- 可视化


## 3. 开发环境
- docker
- jupyter /容器，
- vscode 远程/wsl

## 4. case 2: 单一模块接入：？？
- 物理模块运行机制（Actor）
- 模块 Plugin 机制
    - Python 原生
    - 松耦合
    - 紧耦合

## 5. case 3: 多模块组合：芯部输运
- 输运求解
- Tokamak 类
- 多 Actor 耦合
- 集成工作流

## 6. 小结
- ？？？？

FyTok 用户指南
==============================
## 架构概述

## 数据集成
- 数据格式插件
- 私有数据插件
- 语义映射插件 

## 程序集成
- 模块插件

## 物理集成
- 组装模块

## 装置子系统
- wall
- pf_active 
- ....

## 物理模块
- equilibrium
- core_profiles
- core_sources
- core_transport
- transport solver
- waves

FyTok 开发手册
==============================

## 数据集成 SpDM
- entry,HTree

## 模块开发
- sp_tree 
- Actor/Module

## 物理集成
- Tokamak
- Scenario

## 其他扩展
- 可视化引擎
- 几何
- 网格
- 工作流引擎