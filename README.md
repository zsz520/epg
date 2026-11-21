自动同步到 `gitee`。

**cqcu**

```
https://gitee.com/zsz520/epg/raw/main/cqcu.xml.gz
```

每 `2` 小时检测一次更新。

`files.json` 配置的第三方源由本仓库独立下载到 `epg/`，同时生成 `.xml` 和 `.xml.gz`；根目录由 `epg-src` 发布的文件保持原有发布方式。

下载会跟随重定向，并校验 HTTP 状态、完整 XML、`tv` 根节点及非空频道/节目。单个源失败时保留有效旧文件，其余源继续更新；全部源失败才将任务标记为失败。每次运行的 Actions 摘要会列出各源结果。旧脚本误存的 HTML 等无效缓存会清除，上游恢复后自动重建。`PROXY_URL`（可选）仅用于 livednow；`ACCESS_TOKEN`（可选）用于更新后的 `sync` 通知。

ERW 使用作者公开的 [GitHub 压缩源](https://github.com/kuke31/xmlgz)，下载后解压并保留本仓库原有 `erw.xml` / `erw.xml.gz` 文件名。

**[112114](https://diyp.112114.xyz/)**

```
https://gitee.com/taksssss/tv/raw/main/epg/112114.xml
https://gitee.com/taksssss/tv/raw/main/epg/112114.xml.gz
```

**[老张的 EPG（51zmt）](http://epg.51zmt.top:8000/)**

```
https://gitee.com/taksssss/tv/raw/main/epg/51zmt.xml
https://gitee.com/taksssss/tv/raw/main/epg/51zmt.xml.gz
```

**[erw](https://e.erw.cc/)**

```
https://gitee.com/taksssss/tv/raw/main/epg/erw.xml
https://gitee.com/taksssss/tv/raw/main/epg/erw.xml.gz
```

**[epg.pw](https://epg.pw/index.html)**

```
https://gitee.com/taksssss/tv/raw/main/epg/epgpw_cn.xml
https://gitee.com/taksssss/tv/raw/main/epg/epgpw_cn.xml.gz

https://gitee.com/taksssss/tv/raw/main/epg/epgpw_hk.xml
https://gitee.com/taksssss/tv/raw/main/epg/epgpw_hk.xml.gz

https://gitee.com/taksssss/tv/raw/main/epg/epgpw_tw.xml
https://gitee.com/taksssss/tv/raw/main/epg/epgpw_tw.xml.gz
```

**[livednow](https://assets.livednow.com/guide.html)**

```
https://gitee.com/taksssss/tv/raw/main/epg/livednow.xml
https://gitee.com/taksssss/tv/raw/main/epg/livednow.xml.gz
```

**cqct-iptv / CQCT-IPTV（重庆电信IPTV）**

```
https://raw.githubusercontent.com/zsz520/epg/main/cqct-iptv.xml.gz
```

**fjyd / FJYD-IPTV（福建移动IPTV）**

```
https://raw.githubusercontent.com/zsz520/epg/main/fjyd.xml.gz
```

**yangshipin / YSP-EPG（央视频）**

```
https://raw.githubusercontent.com/zsz520/epg/main/yangshipin.xml.gz
```
