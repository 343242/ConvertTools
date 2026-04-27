# MainWindow Split Plan

## Why split it

`src/ui/main_window.py` 目前同时承担了这些职责：

- 应用壳层：窗口、菜单、状态栏、Dock 布局
- 文件工作流：打开图片、打开 PSD、导出、批量转换入口
- 图层工作流：PSD 图层列表、可见性切换、单图层预览
- 编辑工作流：裁剪、撤销、清除标注、历史栈
- 滤镜工作流：预设滤镜、亮度/对比度/饱和度调整
- 导出设置：格式、质量、压缩和输出目录

这会让 bug 修复、测试和后续功能扩展持续堆到一个文件里。

## Target split

### 1. `ui/controllers/file_controller.py`

负责：

- `_open_file`
- `_load_file`
- `_load_psd`
- `_export_file`
- `_browse_output_dir`
- `_open_batch`
- `_open_batch_with_folder`

依赖：

- `CanvasWidget`
- `ImageConverter`
- `PSDHandler`

### 2. `ui/controllers/layer_controller.py`

负责：

- `_populate_layers`
- `_on_layer_visibility_changed`
- `_preview_layer`

目标：

- 把 PSD 图层面板和主窗口解耦
- 后续可以单独给图层逻辑补测试

### 3. `ui/controllers/filter_controller.py`

负责：

- `_apply_filter_preset`
- `_apply_filter_adjustments`
- `_reset_filter_adjustments`
- `_get_export_options` 中和滤镜相关的共享设置读取

目标：

- 把 Pillow 滤镜逻辑和 UI 控件读取集中起来

### 4. `ui/controllers/history_controller.py`

负责：

- `_push_history`
- `_undo`
- 工具编辑提交后的历史快照策略

目标：

- 明确“哪些动作进入撤销栈”
- 避免后续继续在主窗口里散落 `_push_history()`

### 5. `ui/panels/export_panel.py` / `ui/panels/filter_panel.py`

负责：

- 右侧属性面板的 UI 组装
- 暴露控件引用或结构化配置接口

目标：

- 让 `MainWindow` 只负责布局组合，不负责每个控件的创建细节

## Suggested sequence

1. 先抽 `HistoryController`
2. 再抽 `FileController`
3. 然后抽 `LayerController`
4. 最后把右侧面板拆成 `panels/*`

这样做的原因是：

- `HistoryController` 和本次工具修复直接相关，收益最快
- `FileController` 会显著减少 `MainWindow` 的体积
- `LayerController` 边界清晰，适合独立迁移
- 面板拆分虽然机械，但依赖前面几个控制器的接口稳定

## Non-goals

- 这次不改成 MVC/MVVM 大重构
- 不引入新依赖
- 不在一次提交里把所有 UI 代码全部搬走

## Done criteria for the refactor

- `MainWindow` 只保留窗口装配、菜单绑定和高层协调
- 文件、图层、滤镜、历史逻辑有各自独立模块
- 工具编辑的回归测试不依赖 `MainWindow` 巨型实现细节
