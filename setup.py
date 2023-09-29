from setuptools import find_namespace_packages, setup
import subprocess


version = (subprocess.check_output(["git", "describe", "--always", "--dirty"]).strip().decode("utf-8"))

# Get the long description from the README file
with open("README.md") as f:
    long_description = f.read()

with open("LICENSE.txt") as f:
    license = f.read()

# Get the requirements from the requirements.txt file
with open("requirements.txt") as f:
    requirements = f.read().splitlines()

# Setup the package
setup(
    name="fytok_tutorial",

    version=version,

    description=f"Tutorial of FyTok {version}",

    long_description=long_description,

    url="https://gitee.com/openfusion/fytok_tutorial",

    author="Zhi YU",

    author_email="yuzhi@ipp.ac.cn",

    license=license,

    packages=find_namespace_packages(where="python"),  # 指定需要安装的包

    package_dir={"": "python"},  # 指定包的root目录

    classifiers=[
        "Development Status :: 0 - Beta",
        "Intended Audience :: Plasma Physicists",
        "Topic :: Scientific/Engineering :: Physics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
    ],
    keywords="plasma physics",  # 关键字列表
    python_requires=">=3.10, <4",  # Python版本要求
)
