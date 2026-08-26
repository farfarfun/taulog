# farlog

`farlog` 是一个轻量的 [Loguru](https://github.com/Delgan/loguru) 辅助库，用于按名称拆分日志文件，并提供开箱即用的按日轮转、压缩和保留策略。

## 特性

- 导入包时不创建目录、不写文件，也不修改 Loguru 的全局 handler
- 每个 logger 名称对应一个独立日志文件
- 日志按日轮转，历史文件自动使用 gzip 压缩
- 可选生成聚合日志 `all.log`，同时统一控制台输出格式
- 重复获取同名 logger 不会重复添加 handler
- 兼容旧接口 `getLogger`

## 环境要求

- Python 3.9 或更高版本

## 安装

```bash
pip install farlog
```

## 快速开始

### 仅使用命名日志

直接调用 `get_logger()` 会保留应用已有的 Loguru handler，并在默认的 `logs/` 目录中创建命名日志文件。

```python
from farlog import get_logger

log = get_logger("worker")
log.info("任务开始")
```

生成的文件：

```text
logs/
└── worker.log
```

### 配置控制台和聚合日志

需要统一控制台格式或生成 `all.log` 时，在应用启动阶段显式调用 `configure()`：

```python
from farlog import configure, get_logger

configure("logs")

log = get_logger("worker", level="DEBUG")
log.debug("调试信息")
log.info("任务开始")
```

生成的文件：

```text
logs/
├── all.log
└── worker.log
```

`configure()` 会替换 Loguru 的全局 handler。未绑定 `module_name` 的普通 Loguru 日志仍可正常输出，并在格式中显示为 `-`。

## API

### `configure(log_dir="logs")`

配置彩色控制台输出和聚合日志，并设置后续命名日志使用的目录。

- `log_dir`：日志目录，支持字符串或 `pathlib.Path`
- `all.log`：记录 `INFO` 及以上级别，按日轮转，保留最近 30 个文件
- 如果已经创建过命名 logger，其文件 handler 会切换到新目录

### `get_logger(name="default", level="INFO", formatter=None)`

获取带有独立文件 handler 的 Loguru logger。

- `name`：logger 名称，同时作为日志文件名；只允许普通文件名，不允许传入路径
- `level`：该命名日志文件的最低记录级别
- `formatter`：可选的 Loguru 格式字符串
- 命名日志按日轮转并压缩，保留最近 7 个文件
- 重复调用会复用同名 logger；修改 `level` 或 `formatter` 时会替换旧文件 handler

非法名称会抛出 `ValueError`：

```python
get_logger("../outside")  # ValueError
```

旧接口仍然可用：

```python
from farlog import getLogger

log = getLogger("worker")
```

## 开发

运行回归测试和静态检查：

```bash
python -m unittest discover -s tests -v
ruff check .
```

## 许可证

本项目使用 [MIT License](LICENSE)。
