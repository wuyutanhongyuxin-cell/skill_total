# 抓 bilibili 多 P audio URL 的三种方式

目标产物: `audio_urls.json`，schema 严格固定为：

```json
[
  {"p": 1, "t": "01 标题...", "d": 994, "u": "<primary>", "b": "<backup>"}
]
```

## 方式 A: yt-dlp 直接拿 URL（首选）

```bash
# 列所有 P
yt-dlp --flat-playlist -j "https://www.bilibili.com/video/BV1sZ4y1A7Mq" > playlist.json

# 拿每个 P 的 audio-only 下载链接（不直接下载，只要 URL）
for p in $(seq 1 20); do
  yt-dlp -j --no-playlist \
    --cookies cookies.txt \
    "https://www.bilibili.com/video/BV1sZ4y1A7Mq?p=$p"
done > formats.json
```

然后 jq 解 `formats.json` 里 `acodec=mp4a` 的 entry 拿 `url` + `duration`。

**注意**: bilibili 部分视频需要登录 cookies（大会员视频 / 4K / 限制级）。从浏览器导出 `cookies.txt` 放项目根。

## 方式 B: 浏览器 DevTools 抓包

1. 打开任意一 P 的视频页
2. F12 → Network → 过滤 `bilivideo.com`
3. 切到「音频」清晰度（避免抓到视频流）
4. 点「画质 → 仅音频」让浏览器请求音频流
5. 复制 m4a 请求 URL（含一长串签名参数）
6. 同样的方法逐 P 抓取，**控制在 1 小时内做完，URL 会过期**

把抓到的内容手写成 `audio_urls.json`。

## 方式 C: 已有 b64 解码（仅复用旧项目）

`E:\claude_ask\bilibili_learn\audio_urls.b64` 是旧项目里 base64 编码的备份：

```python
import base64, json, pathlib
b64 = pathlib.Path('audio_urls.b64').read_text()
data = json.loads(base64.b64decode(b64).decode('utf-8'))
pathlib.Path('audio_urls.json').write_text(json.dumps(data, ensure_ascii=False, indent=2))
```

但这套 URL 可能也已过期，跑前测试一两个。

## 校验

`audio_urls.json` 写完后立刻测最浅最深各一条：

```bash
curl -I -L \
  -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
  -H "Referer: https://www.bilibili.com/" \
  "$(jq -r '.[0].u' audio_urls.json)" | head -1
```

应该看到 `HTTP/2 200`。如果是 403 / 404 → URL 已过期或缺 cookies，stage 1 重抓。

## 可选输入: cookies.txt

Netscape 格式（浏览器扩展 EditThisCookie / cookies.txt 都能导出）。
关键字段:
- `SESSDATA`
- `bili_jct`
- `DedeUserID`

放在项目根 `cookies.txt`。`download_all.py` 当前没主动读它，需要时把 curl 命令加 `--cookie cookies.txt`。
