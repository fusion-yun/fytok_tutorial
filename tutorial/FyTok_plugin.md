# Module Plugin 


复杂的模拟通常需要结合许多的物理程序，这些程序可能由社区内不同的研究者提供，并用不同的代码编写。特别是有历史年代的物理程序，或者涉及到许多密集型计算的科学程序和算法，大都使用 C++或者 Fortran 编写的。

为了让他们能够协同工作，需要一个额外的中间层来协调特定的物理代码的执行，并负责数据传递。这一层就是“工作流”。

通常情况下，工作流协调器是用动态编码元素语言实现的，如，FyTok 中选择使用 Python 语言直接来调度不同的物理程序。
这样的话，需要一种“封装器”来帮助本地代码语言和调度协调器语言之间充当介质。使用“封装器”将物理程序封装成统一的调度器的组件，提供统一的 API 来调用和使用这些组件。

因此，FyTok 中提供灵活的插件功能来统一封装和组织用户的第三方物理程序，增加物理程序集成的灵活性，进一步降低程序集成的复杂度。

FyTok 中采用基于插件的模块化设计，这种机制运行将多种语言（如 Fortran，C++，Matlab 等）编写的物理代码集成到以 Python 为主体的复杂计算流程中。
用于构建托克马克的的 Ontology 清楚描述了和托克马克相关的物理概念或者装置组件，称为 Actor.
FyTok 将不同的物理程序绑定到对应的 Actor 上，通过插件机制灵活封装、组织管理、调用。

## 目录结构

第三方物理程序无需将代码打包在 FyTok 的框架内，用户仅需将打包好的代码的目录暴露在 FyTok 可检索的路径下。

该目录按照下述规范的组织结构：

```shell
{work_dir}/python/fytok/plugins/<模块类型>/<物理模块名称>
```

其中：

- {work_dir}是用户本地指定的任意目录
- <模块类型>严格遵守 IMAS 中对物理概念或者装置组件描述的分类，常用的有：

  - equilibrium：efit, freegs, ATEC, FyEq...
  - transport_slover: BITS, FyTrans, onetwo,...
  - core_transport/model: cgyro, glf23, gyro, neo, tglf, tgyro,...
  - core_sources/source: genray, cql3d,...

- <物理程序名称>：第三方物理程序名称

  - 若是程序功能和装置相关，建议程序名称\_装置名称的形式命名，如 efit_east

例如，被集成到 FyTok 中的平衡程序 efit 的目录组织：

```shell
{work_dir}/python/fytok/plugins/equilibrium/efit_east
```

为了方便物理模块的管理、调用和学习推广，FyTok 要求每个物理模块的目录内必须至少包含以下文件：

- README.md：物理模块的说明文档，包含物理模块的功能描述、使用方法、输入输出参数说明等
- `__init__.py`: 物理模块的封装脚本，用于封装原始的物理模块，提供统一的 API，供调度器调用
- `<module_name>.py`：物理模块的封装脚本，用于封装原始的物理模块，提供统一的 API，供调度器调用
- 其他：物理模块的其他文件，如物理模块的源代码、测试用例,配置文件等

以 efit_east 模块为例，

- `__init__.py `

```python
# file: __init__.py
### 指定当前目录efit.east.py文件中需要导入运行环境中的模块 EquilibriumEFITEAST

from .efit_east import EquilibriumEFITEAST

### __all__ 关联一个模块列表，当执行 from xx import * 时，就会导入该列表中指定的所有模块

__all__ = ["EquilibriumEFITEAST"]

```

- `<module_name>.py`

封装后的模块作为 actor 直接作为工作流的组件模块运行，因此，该文件包含以下几个功能：

（1）提供定义明确的应用程序接口，用于工作流中调用，用于 \* 调用用户从系统库或二进制可执行文件中提供的本地代码方法。

    - @Equilibrium.register(["efit_east"]) 明确被集成的物理程序的名称，并将该名称暴露给FyTok.

    - 封装后的actor实质上是一个Python 类，如：class EquilibriumEFITEAST() ，用__init.py__文件进行管理

（2）明确功能逻辑

     - refresh(): 迭代当前时间片，更新最后一个时间片

     - advance(): 推进时间片，更新下一个时间片

（3）向工作流隐藏原始程序的底层运行方式及复杂性

```python
@Equilibrium.register(["efit_east"])
class EquilibriumEFITEAST(FyEqAnalyze):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def refresh(
        self,
        *args,
        time: float | None = None,  # unit: s
        magnetics: Magnetics | None = None,
        pf_active: PFActive | None = None,
        tf: TF | None = None,
        wall: Wall | None = None,
        **kwargs,
    ):
        """update the last time slice, base on profiles_2d[-1].psi, and core_profiles_1d, wall, pf_active"""

    def advance(self, *args, dt=0.1, **kwargs):
        """
        Update the next time slice.
        """
        return super().advance(*args, **kwargs)
```

## 插件调用

- 添加路径到环境变量

```shell

    export PYTHONPATH={work_dir}/python/fytok/plugins/<模块类型>/<物理模块名称>:$PYTHONPATH

```

- 调用：
  IMAS DD 中每个 IDS 都有 code 子节点，用来描述生成此 IDS 的物理代码的通用信息。FyTok 中使用该组织方式来调用代码。
  如下例子，可以在当前环境中查找名称为 efit_east 的 actor，并调用它。

```python
 tok = Tokamak(
        f"east+mdsplus://{WORKSPACE}/fytok_data/mdsplus/~t/?disabled_entry=efit_east&shot={shot}",
        equilibrium={"code": {"name": "efit_east"}}
     )

```
