# Changelog

## 1.1.9

### 新增

（无）

### 修复

- README 环境要求与 `pyproject.toml` `requires-python`/Ruff `target-version` 不一致（README 写 3.9，实际要求 3.10），统一为 Python 3.10。
- `configure()`/`get_logger()` 补充中文 docstring（说明参数、返回值）与 `get_logger()` 返回类型标注。

### 变更

- README 末尾追加组织介绍固定区块。
- `.gitignore` 补充 `*.db`、`*.rar`、`.run/`、`.idea/`、`.vscode/` 规则。

### 废弃

（无）

## 1.1.8 及更早版本

早期版本未维护 CHANGELOG，具体变更参见 git 提交历史。
