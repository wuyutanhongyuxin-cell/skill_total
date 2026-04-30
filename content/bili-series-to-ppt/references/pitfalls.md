# 已踩过的 8 个坑（按出现阶段排序）

## 1. bili2text `'NoneType' object has no attribute 'get'`

**阶段**: stage 3 转写
**症状**: Whisper 显示「已完成 100%」「Detected language: Chinese」之后 bili2text 在「更新索引」步崩溃，进程退出码非 0，但其实 transcripts/original/*.txt **已经写好了**。
**Root cause**: `bili2text/src/b2t/library.py:34` 原代码：

```python
title=result.metadata.get("download", {}).get("title") or result.source.display_name,
```

`pipeline.py` 在 source 是本地音频时把 `metadata["download"] = None` 而**不是不写**这个键。所以 `.get("download", {})` 不会返回 `{}`，而是返回 `None`，下一个 `.get` 就崩了。
**Fix**: 见 `templates/library_patch.diff`。改成 `(result.metadata.get("download") or {}).get("title")`。bili2text 是 editable install，改源即生效，**不要 reinstall**。

## 2. Windows 控制台 GBK 编码崩溃

**阶段**: stage 3
**症状**: bili2text 输出中文时 `UnicodeEncodeError: 'gbk' codec can't encode character`，进程非 0 退出但实际转写已完成。
**Fix**: `os.environ["PYTHONIOENCODING"] = "utf-8"`。`scripts/transcribe_all.py` 已经在 subprocess.run 的 env 里设好。

## 3. Bilibili audio URL 过期 403

**阶段**: stage 2
**症状**: stage 1 抓 URL 一段时间后跑 stage 2，curl 大面积 403 / "redirect: signature failed"。
**Root cause**: bilibili audio mirror URL 的签名 2-6 小时过期。
**Fix**: 重抓 `audio_urls.json`。stage 1 与 stage 2 之间不要拖。

## 4. 下载下来 1MB 但播不开

**阶段**: stage 2
**症状**: `download_one` 返回成功，size > 1MB 通过 size 检查，但播放器打不开。
**Root cause**: bilibili 错误页面也是 1MB+ 的 HTML/JSON，size 检查不够。
**Fix**: 必须 ffprobe 校验时长 ±5s，已在 `download_all.py` 里。

## 5. python-pptx ModuleNotFoundError

**阶段**: stage 7
**症状**: `python scripts/build_ppts.py` 报 `No module named 'pptx'`。
**Root cause**: 系统 python 没装 python-pptx；它装在 `bili2text/.venv` 里。
**Fix**: `uv run --project bili2text python scripts/build_ppts.py`，**不要**给主项目再开 venv。

## 6. subagent 输出的 JSON 解析失败

**阶段**: stage 5 → 6
**症状**: 4 个 agent 出的 20 份 JSON，约 4 份 `json.loads` 报 `Expecting ',' delimiter`。
**Root cause**: 模型在中文 string value 里嵌套未转义 ASCII 双引号：
```
"做题时务必按"X→Y"顺序判别"
```
被 JSON 解析器看成 3 个字符串。
**Fix**: stage 6 跑 `fix_outline_quotes.py`，把内层 `"…"` 替换为 `「…」`。**比让 agent 重写便宜 10 倍**——不要重发 subagent。

## 7. `pptx.Slides` 不能切片

**阶段**: stage 8 校验
**症状**: 想抽前 8 页看看：`prs.slides[:8]` 报 `AttributeError: Slides has no attribute __getitem__`。
**Fix**: 用 enumerate 迭代:
```python
for idx, s in enumerate(prs.slides):
    if idx >= 8: break
    ...
```

## 8. `.b2t/transcripts/original/` 同一个 p 有多份带时间戳的文件

**阶段**: stage 4
**症状**: 重跑过几次的 P01 在 `bili2text/.b2t/transcripts/original/` 下有 `p01-20260428-225700.txt`、`p01-20260429-111800.txt` 等多份。
**Fix**: stage 4 用 `key=lambda f: f.stat().st_mtime` 取最新一份拷到 `transcripts_final/p01.txt`。详见 `SKILL.md` stage 4 代码块。
