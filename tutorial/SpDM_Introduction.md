---
myst:
  substitutions:
    FyTok: _Fy_<font color="blue" />__Tok__
    SpDM: _Sp_<font color="blue" />__DM__
---

# 概述
 
 {{SpDM}} 的设计目标是从 Ontology 出发，将物理模型抽象为 Ontology 中的概念，将物理模型的输入输出抽象为 Ontology 中的属性，将物理模型的参数抽象为 Ontology 中的实例，将物理模型的计算过程抽象为 Ontology 中的关系，将物理模型的计算结果抽象为 Ontology 中的实例。通过将静态数据与具体功能函数/程序绑定，使得用户可以通过简单的配置，实现复杂的数据处理和物理建模。

**SpDM**是一个自主开发的Python库，用于处理EAST数据分析中涉及的多种科学数据格式。它以MAS IDS为标准规范的本体，引入数据集成的思想将以不同语义和格式存储的数据在统一的数据模型下进行检索、查询。

**SpDM**专门为集成建模分析系统FyTok的数据交互而设计，但是不一定与之绑定，独立于 {{FyTok}} 仍然可以使用。
**SpDM**可以读取和处理常用的多种类型的科学数据格式，包括：Python原生的数据格式：字典、List；半结构化数据结构，如：Namelist、JSON、XML、HDF5、netCDF等；结构化数据结构，如：Gdskfile，、Inputfile等；远程数据库系统，如EAST实验的MDSplus及CFETR设计的MDSplus数据库等。{{SpDM}} 将这些数据格式映射在以IMAS IDS为标准的数据交互语义，将数据绑定到 IMAS DD，以便在 IMAS DD 名称空间下统一异构多源数据。但是不依赖于IMAS ，不需要安装IMAS 。{{SpDM}} 读取的数据在内存中以 Python 中数据格式进行交互，其数据的语义是严格遵守 IMAS IDS 的树状结构。{{SpDM}} 也可以将数据写入到常用的多种类型的科学数据格式。
 
**SpDM**可以为用户提供：
- 以IMAS IDS为标准的数据交互语义，将数据绑定到 IMAS DD，以便在 IMAS DD 名称空间下统一异构多源数据。但是不依赖于IMAS ，不需要安装IMAS 。
- 独立的python包，易安装、上手。可独立于ShenMa集群运行，安装在任何有python3.10+的环境下
- 囊括日常科研工作中常用数据格式的处理，且以插件形式管理，开发者用户易对其进行扩展
- 读取的数据在内存中以Python中数据格式进行交互，其数据的语义是严格遵守IMAS IDS的树状结构
- 写数据是灵活的。

## 设计思想  
**SpDM**是一个数据集成工具。它基于标准的数据模型，为用户提供一种全局的中介模式，将来自不同、异构的数据源集成到一个全局的地址空间，通过唯一的URI实现对数据的统一访问，即是数据集成研究的范畴。它的实现，包含三层构架：面向用户的统一访问层及底层的映射层和转化层。
![three-layer](./figures/three-layer_spdb.png)


##  **SpDM的处理对象**

**SpDM**是一个通用的数据集成工具，意在将聚变研究中常用的数据格式都统一映射在标准的语义表述下，同时降低用户处理对不同格式的数据源的门槛。
**SpDM**可以处理常用的多种类型的科学数据格式，包括：
- Python原生的数据格式：字典、List。
    - 直接在内存中交互
- 半结构化数据结构，如：Namelist、JSON、XML、HDF5、netCDF等。
    - 按照半结构化数据的已有的树状路径查询
- 结构化数据结构，如：Gdskfile，、Inputfile等。
    - 数据量比较小，拿回来全部放在内存中，直接访问。
- 远程数据库系统，如EAST实验的MDSplus及CFETR设计的MDSplus数据库等。
    - 将原始的数据源映射在标准的树状结构的语义下。
    - 支持延迟执行
    - 支持不同类型数据的集成，统一的入口访问。
        - 静态装置描述数据
        - 动态实验测量数据


        
<table>
    <tr>
        <td><b>数据格式</b></td>
        <td><b>插件名称</b> </td>
        <td><b>format标识</b></td>
        <td><b>映射和转化</b></td>
        <td><b>备注</b></td>
    </tr>
    <tr>
        <td rowspan="1">内存中数据</td>
        <td>无</td>
        <td>Dict，List</td>
        <td>无</td>
        <td>无</td>
    </tr>
    <tr>
        <td rowspan="3">非结构化数据</td>
        <td>plugin_gdskfile</td>
        <td>["gfile", "gdskfile"，“GDSKfile”]</td>
        <td>无界限</td>
        <td>数据直接读入内存</td>
    </tr>
    <tr>
        <td>plugin_namelist </td>
        <td>["namelist"] </td>
        <td>无界限</td>
        <td>数据直接读入内存</td>
    </tr>
    <tr>
        <td>......</td>
        <td>......</td>
        <td>......</td>
        <td>......</td>
    </tr>
    <tr>
        <td rowspan="5">半结构化数据</td>
        <td>plugin_netcdf</td>
        <td>["nc", "netcdf", "NetCDf"]</td>
        <td>分开</td>
        <td>延迟执行</td>
    </tr>
    <tr>
        <td>plugin_hdf5 </td>
        <td>["h5", "hdf5", "HDF5"]</td>
        <td>分开</td>
        <td>延迟执行</td>
    </tr>
    <tr>
        <td>plugin_json</td>
        <td> ["json", "JSON"]  </td>
        <td>分开</td>
        <td>延迟执行</td>
    </tr>
    <tr>
        <td>plugin_yaml </td>
        <td>["yaml", "YAML"]  </td>
        <td>分开</td>
        <td>延迟执行</td>
    </tr>
    <tr>
        <td>plugin_xml</td>
        <td> ["xml"] </td>
        <td>分开</td>
        <td>延迟执行</td>
    </tr>
    <tr>
        <td rowspan="2">远程数据库系统</td>
        <td>plugin_mdsplus</td>
        <td>["mdsplus", "mds", "mds+", "MDSplus"]</td>
        <td>分开</td>
        <td>wall,pf_active,tf,magnetics,eq</td>
    </tr>
    <tr>
        <td>......</td>
        <td>......</td>
        <td>......</td>
        <td>......</td>
    </tr>

</table>
