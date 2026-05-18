# UTF-8 zip 打包细节与陷阱

> 阶段 6 的全部落地。Windows 中文文件名 + 跨平台解压不乱码的解法。

## 1. zip 内部结构（固定）

```
作业N_<topic>_提交.zip
├── 设计说明.md
├── 代码/
│   ├── dashboard.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── palette.py
│   │   ├── theme.py
│   │   ├── data_loader.py
│   │   ├── <category_map>.py
│   │   └── <entity_geo>.py
│   ├── extras/
│   │   ├── __init__.py
│   │   ├── 01_<图名>.py
│   │   ├── 02_<图名>.py
│   │   └── ... 0N_<图名>.py
│   └── tests/
│       ├── __init__.py
│       └── test_*.py
└── 图片/
    ├── 00_<dashboard>.png
    ├── 01_<图名>.png ... 0N_<图名>.png
    ├── 原生_<图名>.png
    └── 原生_<统计>.csv
```

**红线**：
- 设计说明.md 在**顶层**而非「代码/」下——评分老师第一眼就要看到
- 教师原生产物用「原生_」前缀，与作业产出图区分
- `__init__.py` 必须打进 zip，否则解压后 Python import 失败

## 2. 打包脚本模板

```python
"""重打 提交 zip"""
import zipfile
from pathlib import Path

ROOT = Path(__file__).parent
VIZ = ROOT / "visualization"
OUT_ZIP = ROOT / "作业N_<topic>_提交.zip"

# (源文件绝对路径, zip 内相对路径)
manifest = []

# 顶层：设计说明
manifest.append((VIZ / "设计说明.md", "设计说明.md"))

# 代码/
manifest.append((VIZ / "dashboard.py", "代码/dashboard.py"))

for p in (VIZ / "core").glob("*.py"):
    manifest.append((p, f"代码/core/{p.name}"))

for p in sorted((VIZ / "extras").glob("*.py")):
    manifest.append((p, f"代码/extras/{p.name}"))

for p in sorted((VIZ / "tests").glob("*.py")):
    manifest.append((p, f"代码/tests/{p.name}"))

# 图片/ + 原生产物
for p in sorted((VIZ / "outputs").glob("*.png")):
    manifest.append((p, f"图片/{p.name}"))
for p in sorted((VIZ / "outputs").glob("*.csv")):
    manifest.append((p, f"图片/{p.name}"))

# 写 zip
if OUT_ZIP.exists():
    OUT_ZIP.unlink()

with zipfile.ZipFile(OUT_ZIP, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for src, dst in manifest:
        if not src.exists():
            print(f"[MISS] {src}")
            continue
        z.write(src, arcname=dst)
        print(f"[+] {dst}  ({src.stat().st_size // 1024} KB)")

print(f"\n[DONE] {OUT_ZIP.name}  ({OUT_ZIP.stat().st_size // 1024} KB, "
      f"{len(manifest)} 文件)")
```

**红线**：
- 用 **manifest 显式列表**而不是 `glob("**/*")`——后者会把 `__pycache__/`、`.pytest_cache/` 等一起打进去
- `compresslevel=6` 是速度与压缩比的平衡点
- 写之前 `if exists: unlink`——zip 模式 `"w"` 会复用旧 entry，导致冗余

## 3. UTF-8 文件名陷阱

### 问题

Windows 默认用 cp437/GBK 编码 zip 内文件名。中文路径会变成 `Ô´Éú_ÌÆÊ«...png` 这种乱码。

### 解法

Python 3.x 的 `zipfile.ZipFile.write` 在 Python 3.6+ 自动给 ZipInfo 设置 UTF-8 flag（bit 0x800），但**只有当文件名实际不是 ASCII 时才设**。直接用上面的模板就够。

### 验证

```python
import zipfile

with zipfile.ZipFile(OUT_ZIP) as z:
    bad = []
    for zi in z.infolist():
        utf8 = bool(zi.flag_bits & 0x800)
        if not utf8 and any(ord(c) > 127 for c in zi.filename):
            bad.append(zi.filename)
    if bad:
        raise RuntimeError(f"以下文件名缺 UTF-8 标志位：{bad}")
    print(f"[OK] {len(z.infolist())} 个条目 UTF-8 标志位全部正确")
```

**红线**：bit 0x800 验证未通过 → **不**发给用户，回打包脚本检查。

## 4. 跨平台解压测试

虽然 Python 3.x 写 zip 默认 UTF-8 OK，但接收方解压工具也要支持：

| 解压工具 | UTF-8 文件名支持 |
|---|---|
| Windows 11 资源管理器 | ✅ 原生支持 |
| 7-Zip ≥ 15.05 | ✅ 自动检测 |
| 360 压缩 / WinRAR | ✅ 现代版本支持 |
| macOS Finder | ✅ |
| `python -m zipfile -e` | ✅ |
| Windows 7 资源管理器 | ❌ 会乱码（建议提示用 7-Zip） |

**红线**：如果交付对象明确是 Windows 7 用户，需在 caption 里注明"请用 7-Zip / WinRAR 解压"。

## 5. SendUserFile 交付

```python
# 在 Python 之外（你作为助手）调用
SendUserFile(
    files=["E:\\...\\作业N_<topic>_提交.zip"],
    status="proactive",
    caption=f"最终提交包 {size_mb:.2f} MB · {n_files} 文件"
            f"（设计说明 + 代码 + 图片）",
)
```

**红线**：
- `status="proactive"`——这是主动交付不是回答用户问题
- caption 必须含：大小 + 文件数 + 简要构成
- 不附带"接下来要做 X"——任务结束就是结束

## 6. 常见漏装项（按出现频率）

| 漏装 | 症状 | 防御 |
|---|---|---|
| `__init__.py` | 解压后 `import core.palette` 失败 | manifest 显式 `glob("*.py")` 包括它 |
| 原生 csv | 教师"已认证"产物缺失 | 阶段 0 笔记里标 `[必打入zip]` |
| 设计说明.md | 顶层评分入口缺失 | manifest 第一行就是它 |
| `data/` 目录 CSV | 解压后 dashboard.py 跑不起来 | 默认**不**打 data/——zip 是提交不是可复现包；如要可复现需在设计说明声明 data 路径 |
| 字体文件 | 接收方机器没装中文字体 | 不打字体——5 级降级机制自己降；设计说明声明字体要求 |

**红线**：`data/<corpus>_with_sentiment.csv` 默认**不**打入提交 zip——CSV 通常很大（几 MB+）且评分老师不会真跑你的脚本。但要在设计说明里**声明**：「数据 CSV 由原生 `sentiment.py` 产出，路径 `visualization/data/`」。

## 7. zip 大小预算

| 部分 | 量级 |
|---|---|
| 设计说明.md | 8-15 KB |
| 代码（core+extras+tests+dashboard） | 50-150 KB |
| 图片（12 PNG + 1 CSV，@300dpi） | 5-15 MB |
| **总和** | **5-15 MB** |

超过 20 MB 检查：
- 是否误打了 `.pytest_cache/` 或 `__pycache__/`
- 是否误打了 `data/` CSV
- 是否某张 PNG @300dpi 出图过大（共现网络 spring_layout 复杂时可能 3+ MB，正常）

## 8. 终局检查清单

```bash
# 1. 打包脚本 stdout 看每行 [+] 都有 size
python rebuild_zip.py

# 2. UTF-8 验证脚本
python verify_zip_utf8.py    # 跑 § 3 的验证代码

# 3. 列出 zip 内容（PowerShell）
python -c "import zipfile; [print(f'{zi.file_size//1024:>6} KB  {zi.filename}') for zi in zipfile.ZipFile('作业N_<topic>_提交.zip').infolist()]"

# 4. 抽样解压一个中文文件名验证
python -m zipfile -e 作业N_<topic>_提交.zip /tmp/test_unzip
ls /tmp/test_unzip
```

四项全过 → SendUserFile。
