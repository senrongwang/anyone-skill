# Archive — 归档代码

本目录存放 Anyone Skill 项目中不再使用但保留历史参考价值的文件和代码。

## 归档内容

### `tools/`

| 文件 | 原因 |
|------|------|
| `qq_parser.py` | 未被任何模块导入；QQ 聊天记录的解析功能已在 `create_persona.py` 内联实现 |
| `social_parser.py` | 未被任何模块导入；社交媒体内容的处理已在 `create_persona.py` 内联实现 |
| `version_manager.py` | 未被任何模块导入；版本管理未集成到主流程中 |

### `docs/`

| 文件 | 原因 |
|------|------|
| `INSTALL.md` | 过时的 Claude Code 安装说明，项目已改为纯 API 方式运行 |

### `qoder/`

| 内容 | 原因 |
|------|------|
| `.qoder/` | Qoder 工具自动生成的 Wiki 文档，非项目代码 |

## 恢复方式

如需恢复某个文件，将其移回原位置：

```bash
# 示例：恢复 version_manager.py
mv archive/tools/version_manager.py tools/
```
