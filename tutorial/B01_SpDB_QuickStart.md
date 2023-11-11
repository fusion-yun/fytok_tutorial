## SpDB Manual

### 概述
SpDB是一个自主开发的Python库，用于处理EAST数据分析中涉及的多种科学数据格式。它以MAS IDS为标准规范的本体，引入数据集成的思想将以不同语义和格式存储的数据在统一的数据模型下进行检索、查询。

SpDB专门为集成建模分析系统FyTok的数据交互而设计，但是不一定与之绑定，独立于FyTok仍然可以使用。

SpDB可以为用户提供：
- 以IMAS IDS为标准的数据交互语义，将数据绑定到 IMAS DD，以便在 IMAS DD 名称空间下统一异构多源数据。但是不依赖于IMAS ，不需要安装IMAS 。
- 独立的python包，易安装、上手。可独立于ShenMa集群运行，安装在任何有python3.10+的环境下
- 囊括日常科研工作中常用数据格式的处理，且以插件形式管理，开发者用户易对其进行扩展
- 读取的数据在内存中以Python中数据格式进行交互，其数据的语义是严格遵守IMAS IDS的树状结构
- 写数据是灵活的。

### 安装SpDB
#### ShenMa集群上的SpDB 模块
目前，ShenMa集群内（service108）服务器上SpDB模块是可用的。你能运行下面命令，加载其环境：


```
module load spdm/0.0.0-foss-2022b
```

另外，如果你想使用MDSplus 后端，需要load：


```
module load MDSplus-Python/7.131.5-gfbf-2022b-Python-3.10.8
```

测试安装：


```
python -c "import spdm; print(spdm.__version__)"
```

#### 个人Python环境本地安装
推荐使用anconda维护个人Python环境，Python版本3.10+。
SpDB的发行包已上传在pip 仓库中，运行pip install直接安装:


```
pip install --upgrade pip
pip install spdm 
```

或者，也可以下载打包好的whl源码包安装：


```
wget https://gitee.com/SimPla/SpDM/releases/tag/0.3.0-rc
pip install --upgrade pip
pip install spdm 
```

如果pip安装指定了安装目录，需先添加安装目录到PYTHONPATH中。否者在默认的~/.local/lib/下面：


```
export PYTHONPATH=${INSTALLPATH}/site-packages:${PYTHONPATH}
```

测试你的安装：


```
cd ~
python -c "import spdm; print(spdm.__version__)"
```
