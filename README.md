# Word Learner - 背单词小工具

一个基于 PyQt6 的桌面单词学习应用程序，帮助您高效地学习和记忆英语单词。

## ✨ 功能特性

### 🎯 核心功能
- **智能显示模式**: 支持随机显示和顺序显示两种模式
- **自动播放**: 可设置自动切换单词的时间间隔
- **中英文切换**: 可选择是否显示中文翻译
- **响应式界面**: 字体大小根据窗口大小自动调整

### 📚 单词管理
- **添加单词**: 支持添加英文单词、中文翻译和词性
- **编辑单词**: 可编辑当前显示的单词信息
- **删除单词**: 通过输入英文单词来删除指定词汇
- **搜索功能**: 在右上角搜索框中快速查找单词

### ⚙️ 个性化设置
- **显示间隔**: 自定义自动切换单词的时间间隔
- **显示模式**: 选择随机显示或顺序显示
- **中文显示**: 控制是否显示中文翻译

## 🚀 快速开始

### 系统要求
- Python 3.12 或更高版本
- 支持的操作系统: Windows, macOS, Linux

### 安装步骤

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd word_learner
   ```

2. **创建虚拟环境**
   ```bash
   # 如果使用 uv
   uv venv
   source .venv/bin/activate  # Linux/macOS
   .venv\Scripts\activate     # Windows

   # 或使用传统方式
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   .venv\Scripts\activate     # Windows
   ```

3. **安装依赖**
   ```bash
   # 如果使用 uv
   uv pip install -e .

   # 或使用 pip
   pip install -e .
   ```

4. **运行程序**
   ```bash
   uv run python main.py
   ```

## 📖 使用指南

### 基本操作

1. **启动应用**: 运行 `uv run python main.py` 启动程序
2. **查看单词**: 程序会自动显示单词，包括英文、词性和中文翻译
3. **手动切换**: 点击"下一个"按钮手动切换到下一个单词
4. **搜索单词**: 在右上角搜索框输入英文或中文进行查找

### 菜单功能

#### 文件菜单
- **添加单词 (Ctrl+A)**: 添加新的单词到词库
- **编辑单词 (Ctrl+E)**: 编辑当前显示的单词
- **删除单词 (Ctrl+D)**: 删除指定的单词
- **设置 (Ctrl+S)**: 打开设置对话框
- **退出**: 关闭应用程序

#### 帮助菜单
- **关于**: 显示应用程序信息

### 快捷键
- `Ctrl + A`: 添加单词
- `Ctrl + E`: 编辑单词
- `Ctrl + D`: 删除单词
- `Ctrl + S`: 打开设置
- `Enter`: 在搜索框中执行搜索

## 📁 项目结构

```
word_learner/
├── main.py                 # 程序入口点
├── config.json            # 配置文件
├── pyproject.toml         # 项目配置
├── uv.lock               # 依赖锁定文件
├── .python-version       # Python版本指定
├── .gitignore           # Git忽略文件
├── README.md            # 项目说明文档
├── assets/              # 资源文件
│   └── words.json       # 单词数据库
└── src/                 # 源代码目录
    ├── __init__.py
    ├── core/            # 核心逻辑模块
    │   ├── __init__.py
    │   ├── settings_manager.py    # 设置管理器
    │   └── word_manager.py        # 单词管理器
    └── ui/              # 用户界面模块
        ├── __init__.py
        ├── main_window.py         # 主窗口
        ├── settings_dialog.py     # 设置对话框
        └── word_editor_dialog.py  # 单词编辑对话框
```

## 🔧 配置说明

### config.json 配置文件
```json
{
  "display_interval": 3,     // 显示间隔（秒）
  "display_mode": "random",  // 显示模式: "random" 或 "sequential"
  "show_chinese": true       // 是否显示中文翻译
}
```

### words.json 数据格式
```json
[
  {
    "word": "example",           // 英文单词
    "translation": "例子",       // 中文翻译
    "partOfSpeech": "n."        // 词性（可选）
  }
]
```

## 🛠️ 开发说明

### 架构设计
- **模块化设计**: 核心逻辑与UI界面分离
- **MVC模式**: 数据管理、业务逻辑和界面展示分离
- **配置管理**: 统一的设置管理机制

### 主要组件
- **WordManager**: 负责单词数据的CRUD操作
- **SettingsManager**: 负责应用配置的管理
- **MainWindow**: 主界面，协调各个组件
- **对话框组件**: 处理用户交互

### 代码特点
- 详细的中文注释
- 完善的错误处理
- 响应式UI设计
- 数据持久化

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本项目
2. 创建特性分支: `git checkout -b feature/new-feature`
3. 提交更改: `git commit -am 'Add new feature'`
4. 推送分支: `git push origin feature/new-feature`
5. 提交 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 LICENSE 文件了解详细信息。

## 🎯 未来计划

- [ ] 添加单词发音功能
- [ ] 支持多种语言
- [ ] 添加学习进度统计
- [ ] 支持单词分类管理
- [ ] 添加记忆曲线算法
- [ ] 支持导入/导出词库

## 📞 联系方式

如有问题或建议，请通过 GitHub Issues 联系我们。

---

**Enjoy Learning! 🎉**
