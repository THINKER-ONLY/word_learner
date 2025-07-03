from cx_Freeze import setup, Executable
import sys

# 包含的文件和目录
include_files = [
    ("assets/words.json", "assets/words.json"),
    ("src/", "src/"),
]

# 构建选项
build_options = {
    "packages": ["PyQt6", "PyQt6.QtWidgets", "PyQt6.QtCore", "PyQt6.QtGui"],
    "include_files": include_files,
    "excludes": ["tkinter", "matplotlib", "numpy", "pandas"],  # 排除不需要的包
    "optimize": 2,  # 优化级别
}

# 可执行文件配置
executables = [
    Executable(
        "main.py",
        base="Win32GUI" if sys.platform == "win32" else None,  # 隐藏控制台窗口
        target_name="WordLearner.exe",
        icon=None  # 如果有图标文件，可以在这里指定路径
    )
]

setup(
    name="Word Learner",
    version="0.1.0",
    description="基于PyQt6的桌面单词学习工具",
    options={"build_exe": build_options},
    executables=executables
) 