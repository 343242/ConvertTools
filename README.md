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

推荐使用仓库里的 Windows 构建脚本。它会使用干净 PATH 构建，避免 Anaconda / MSYS2 / Git `usr\bin` 等环境中的 DLL 被误打进发布包，并在构建后自动验包：

脚本路径：`scripts/build_windows.ps1`

```powershell
.\scripts\build_windows.ps1
```

构建脚本会在完成后调用：

脚本路径：`scripts/verify_dist.ps1`

```powershell
.\scripts\verify_dist.ps1
```

验包会检查 `dist/ConvertTools/` 中是否出现已知污染 DLL（例如 `icu*.dll`），确认 Qt Windows 平台插件存在，并启动一次 `ConvertTools.exe` 检查 `%LOCALAPPDATA%\ConvertTools\startup-error.log` 是否生成。

如需只验包不重新构建：

```powershell
.\scripts\verify_dist.ps1
```

也可以手动构建，但不推荐在复杂 Windows 环境下直接使用当前 shell 的 PATH：

```bash
uv run pyinstaller ConvertTools.spec --noconfirm
```

输出目录：`dist/ConvertTools/ConvertTools.exe`

### 制作安装程序（推荐）

可以直接分发 `dist/ConvertTools/` 整个目录，但更推荐在 Windows 上再打一个安装包。

#### 方案 1：NSIS

仓库已提供 NSIS 脚本：[installer.nsi](./installer.nsi)

先确保已经完成 PyInstaller 构建，目录存在：

```text
dist/ConvertTools/ConvertTools.exe
```

然后执行：

```bash
makensis installer.nsi
```

如果 `makensis` 不在 PATH 里，就用 NSIS 安装目录下的完整路径，例如：

```bash
& "C:\Program Files (x86)\NSIS\makensis.exe" /INPUTCHARSET UTF8 "installer.nsi"
```

输出安装包：

```text
dist/ConvertTools-Setup.exe
```

安装包现在支持三种安装方式：

- `完整安装`：核心文件 + 开始菜单快捷方式 + 桌面快捷方式
- `最小安装`：仅安装核心文件
- `自定义安装`：可手动选择安装目录、开始菜单快捷方式、桌面快捷方式

在 `自定义安装` 模式下，用户可以：

- 修改安装路径
- 选择是否创建开始菜单快捷方式
- 选择是否创建桌面快捷方式

默认行为：

- 安装到 `C:\Program Files\ConvertTools`
- 完整安装时创建开始菜单快捷方式
- 完整安装时创建桌面快捷方式
- 写入卸载程序 `Uninstall.exe`

#### 方案 2：Inno Setup

如果你更习惯 Inno Setup，也可以继续使用 [Inno Setup](https://jrsoftware.org/isinfo.php)：

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
- 分发时不要只拷贝单个 `ConvertTools.exe`，而应分发整个 `dist/ConvertTools/` 目录，或使用上面的安装包
- 如果安装后的程序启动失败，Windows 版本会把启动日志写到 `%LOCALAPPDATA%\ConvertTools\startup-error.log`
