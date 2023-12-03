#### 执行过程（eq_demo.py——> eq.refesh(在efit.py里面)）：
- 这个说明文档是对应于用户的，怎么添加一个物理模块进来。
1. demo-efit.py
    - 准备输入IDS文件，通过SpDB读取获得
        - open_entry() 得到几个IDS：magnetics,pf_avtivate,tf

2. 定义平衡
```
equilibrium = Equilibrium(
    {**scenario["equilibrium"],
        "code": {
            "name": "efit",  # 指定 equlibrium 模块 "eq_analyze",
            "parameters": {"boundary": "fixed", }},
        "$default_value": {
            "time_slice": {   # 默认参数， time_slice 是 TimeSeriesAoS
                "boundary": {"psi_norm": 0.99},
                "profiles_2d": {"grid": {"dim1": 256, "dim2": 128}},
                "coordinate_system": {"grid": {"dim1": 128, "dim2": 128}}
            }}},

    wall=wall,
    pf_active=pf_active
)
```

3. 更新平衡
equilibrium.refresh(manetics,pf_activate,tf)
4. 画出平衡
    ```
        display(  # plot equilibrium
        equilibrium,
        title=f" time={equilibrium.time}s",
        output=output_path/"tokamak_post.svg")
    ```

### plugin中efit模块
class EquilibriumEFIT(FyEqAnalyze)：
    def __init__():
        pass

    def _get_mdsdata(manetics,pf_activate,tf):
        .....
        mdsdata = Data() 
        return mdsdata

    def solve():

        from EQEFIT import efit 
        mdsdata = _get_mdsdata(**kwargs)
##### 需要打包成efit.run ，给它一个实验数据就可以生成gile文件。
不要用命令行,直接改为参数.
    efit.run(mdsdata) =-> gfile 文件
def refresh():
    准备参数，ids变成mdsdata4efit
    self.solve(mdsdata4efit)
    to_imas()

#### 工作目录
- 指定工作目录，不然默认在当前目录下。