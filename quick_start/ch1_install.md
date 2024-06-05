# 运行环境和安装

## 建议运行环境

- 语言 Python >= 3.10/3.11 （FyTok 为纯Python包，但物理模块依赖操作系统）
- 操作系统： Ubuntu 22.04   （模块运行开发环境）

### Windows 11 系统解决方案：
- Windows Subsystem for Linux  （WSL2）
- WSL安装： 打开 PowerShell 
```{powershell}
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux # 打开WSL支持
wsl --set-default-version 2           # 指定wsl的版本
wsl --install -d Ubuntu-22.04         #（指定安装版本）
wsl --list --online                   # 查看可用的Linux发行版版
wsl -l -v                             # 查看wsl的版本
wsl --set-version Ubuntu-22.04 2      # 指定Linux发行版
```

## 集成开发环境 

- 在 Ubuntu 22.04 下安装 JupyterLab
```{bash}
sudo apt-get install python3 python3-pip 
pip install jupyterlab
```
- 在 Windows 上安装 Visual Studio Code（不是在 WSL 文件系统中）。
VSCode安装扩展包 ：
   - WSL
   - Python
   - Jupyter 
   - VSCode中打开WSL：
   - 打开 VSCode，左下角选择链接到 WSL
   - 或者 ctrl+shift+p 调出命令面板，选择链接WSL


## 安装 FyTok

- 在 Ubuntu 22.04 下
```{bash}
pip install fytok
```
- 检查安装：
```{bash}
python -c "import fytok"
```
- 测试基本环境·
    - ctrl+shif+p 打开 notebook

```{bash}
from fytok.tokamak import Tokamak
```