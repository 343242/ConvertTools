# ConvertTools

本地图片格式转换与编辑工具，支持 PSD 解析、图层预览、画布操作和批量转换。

## 功能

- **格式转换**: PNG / JPEG / WebP / BMP / TIFF / ICO / GIF 互转，近无损质量
- **PSD 支持**: 解析 PSD 文件，图层预览、可见性切换、图层导出
- **画布操作**: 鼠标滚轮缩放、拖拽平移
- **编辑工具**: 裁剪、矩形/箭头/文字标注、自由画笔涂抹
- **滤镜**: 亮度/对比度/饱和度调节 + 灰度/怀旧/反色/模糊/锐化预设
- **批量转换**: 多文件队列，后台线程转换，支持暂停/取消
- **拖放**: 直接拖拽文件到窗口打开
- **安全**: 仅本地运行，保留源文件不修改

## 安装

需要 Python 3.11+ 和 [uv](https://docs.astral.sh/uv/)。

```bash
uv sync
```

## 运行

```bash
uv run python main.py
```

## 快捷键

| 功能 | 快捷键 |
|------|--------|
| 打开文件 | Ctrl+O |
| 导出 | Ctrl+S |
| 批量转换 | Ctrl+B |
| 选择工具 | V |
| 平移工具 | H |
| 裁剪工具 | C |
| 矩形标注 | R |
| 箭头标注 | A |
| 文字标注 | T |
| 画笔工具 | B |
| 放大 | +/= |
| 缩小 | - |
| 适应窗口 | Ctrl+0 |
| 撤销 | Ctrl+Z |
| 应用裁剪 | Enter |

## 技术栈

- **GUI**: PySide6 (Qt6)
- **图片处理**: Pillow
- **PSD 解析**: psd-tools

## 打包为 .exe

### 前置条件

在 **Windows** 环境下操作（WSL/Linux 打包生成的是 Linux 可执行文件）：

1. 安装 [Python 3.11+](https://www.python.org/downloads/) 和 [uv](https://docs.astral.sh/uv/)
2. 克隆项目后执行：

```bash
uv sync
```

### 构建可执行文件

```bash
uv run pyinstaller ConvertTools.spec --noconfirm
```

输出目录：`dist/ConvertTools/ConvertTools.exe`

### 制作安装程序（可选）

使用 [Inno Setup](https://jrsoftware.org/isinfo.php) 或 [NSIS](https://nsis.sourceforge.io/) 将 `dist/ConvertTools/` 目录打包为安装程序：

**Inno Setup 示例** (`installer.iss`)：

```ini
[Setup]
AppName=ConvertTools
AppVersion=0.1.0
DefaultDirName={pf}\ConvertTools
DefaultGroupName=ConvertTools
OutputBaseFilename=ConvertTools-Setup
Compression=lzma2/ultra64

[Files]
Source: "dist\ConvertTools\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs

[Icons]
Name: "{group}\ConvertTools"; Filename: "{app}\ConvertTools.exe"
Name: "{commondesktop}\ConvertTools"; Filename: "{app}\ConvertTools.exe"
```

### 注意事项

- 打包已排除：测试代码 (`tests/`)、开发工具 (`pytest`)、`.omc/`、`.claude/`、`.venv/`
- 预期产物大小：~190MB（主要来自 Qt 运行时）
- 如需进一步压缩体积，可在 spec 文件 `excludes` 中添加更多不需要的 Qt 模块
