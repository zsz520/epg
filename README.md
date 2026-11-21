# EPG 节目单

本仓库提供 XMLTV 节目单文件。第三方源下载到 `epg/`，由 [epg-src](https://github.com/zsz520/epg-src) 采集发布的文件位于根目录。

## 第三方节目单

按 [files.json](files.json) 配置，每 **2 小时**检查一次更新，也可在 [GitHub Actions](https://github.com/zsz520/epg/actions/workflows/epg.yml) 手动运行。每个源同时提供 `.xml` 和 `.xml.gz`，压缩上游会先解压校验，输出文件名保持固定。

将下表中的 XML 或 GZ 链接复制到支持 XMLTV 的播放器中即可使用。

| 来源 | 文件名 | XML | GZ | 上游地址 |
| --- | --- | --- | --- | --- |
| 112114 | `112114.xml` | [XML](https://raw.githubusercontent.com/zsz520/epg/main/epg/112114.xml) | [GZ](https://raw.githubusercontent.com/zsz520/epg/main/epg/112114.xml.gz) | [上游](https://epg.112114.xyz/pp.xml.gz) |
| 老张 EPG · e | `51zmt.xml` | [XML](https://raw.githubusercontent.com/zsz520/epg/main/epg/51zmt.xml) | [GZ](https://raw.githubusercontent.com/zsz520/epg/main/epg/51zmt.xml.gz) | [上游](http://epg.51zmt.top:8000/e.xml) |
| 老张 EPG · e1 | `51zmte1.xml` | [XML](https://raw.githubusercontent.com/zsz520/epg/main/epg/51zmte1.xml) | [GZ](https://raw.githubusercontent.com/zsz520/epg/main/epg/51zmte1.xml.gz) | [上游](http://epg.51zmt.top:8000/e1.xml.gz) |
| 老张 EPG · e2 | `51zmte2.xml` | [XML](https://raw.githubusercontent.com/zsz520/epg/main/epg/51zmte2.xml) | [GZ](https://raw.githubusercontent.com/zsz520/epg/main/epg/51zmte2.xml.gz) | [上游](http://epg.51zmt.top:8000/e2.xml.gz) |
| ERW · 七天回看（含当天） | `erw.xml` | [XML](https://raw.githubusercontent.com/zsz520/epg/main/epg/erw.xml) | [GZ](https://raw.githubusercontent.com/zsz520/epg/main/epg/erw.xml.gz) | [上游](https://raw.githubusercontent.com/kuke31/xmlgz/main/all.xml.gz) |
| epg.pw · 中国大陆 | `epgpw_cn.xml` | [XML](https://raw.githubusercontent.com/zsz520/epg/main/epg/epgpw_cn.xml) | [GZ](https://raw.githubusercontent.com/zsz520/epg/main/epg/epgpw_cn.xml.gz) | [上游](https://epg.pw/xmltv/epg_CN.xml.gz) |
| epg.pw · 中国香港 | `epgpw_hk.xml` | [XML](https://raw.githubusercontent.com/zsz520/epg/main/epg/epgpw_hk.xml) | [GZ](https://raw.githubusercontent.com/zsz520/epg/main/epg/epgpw_hk.xml.gz) | [上游](https://epg.pw/xmltv/epg_HK.xml.gz) |
| epg.pw · 中国台湾 | `epgpw_tw.xml` | [XML](https://raw.githubusercontent.com/zsz520/epg/main/epg/epgpw_tw.xml) | [GZ](https://raw.githubusercontent.com/zsz520/epg/main/epg/epgpw_tw.xml.gz) | [上游](https://epg.pw/xmltv/epg_TW.xml.gz) |

ERW 使用作者公开的 [GitHub 压缩源](https://github.com/kuke31/xmlgz)。Livednow 已从当前配置移除。

## epg-src 发布文件

以下文件由采集端发布，沿用各自的更新安排，独立于 `files.json` 下载任务。仅列出仓库当前已有的格式。

| 来源 | XML | GZ |
| --- | --- | --- |
| cqcu | — | [GZ](https://raw.githubusercontent.com/zsz520/epg/main/cqcu.xml.gz) |
| CQCT-IPTV（重庆电信 IPTV） | [XML](https://raw.githubusercontent.com/zsz520/epg/main/cqct-iptv.xml) | [GZ](https://raw.githubusercontent.com/zsz520/epg/main/cqct-iptv.xml.gz) |
| FJYD-IPTV（福建移动 IPTV） | [XML](https://raw.githubusercontent.com/zsz520/epg/main/fjyd.xml) | [GZ](https://raw.githubusercontent.com/zsz520/epg/main/fjyd.xml.gz) |
| YSP-EPG（央视频） | [XML](https://raw.githubusercontent.com/zsz520/epg/main/yangshipin.xml) | [GZ](https://raw.githubusercontent.com/zsz520/epg/main/yangshipin.xml.gz) |
| SDGD-EPG（山东广电） | [XML](https://raw.githubusercontent.com/zsz520/epg/main/sdgd.xml) | [GZ](https://raw.githubusercontent.com/zsz520/epg/main/sdgd.xml.gz) |
| bjiptv | — | [GZ](https://raw.githubusercontent.com/zsz520/epg/main/bjiptv.xml.gz) |
| chuanliu | — | [GZ](https://raw.githubusercontent.com/zsz520/epg/main/chuanliu.xml.gz) |
| cqlaidian | — | [GZ](https://raw.githubusercontent.com/zsz520/epg/main/cqlaidian.xml.gz) |
| migu | — | [GZ](https://raw.githubusercontent.com/zsz520/epg/main/migu.xml.gz) |

## 更新与异常处理

- 下载会跟随重定向，检查 HTTP 状态、XML 完整性、`tv` 根节点和非空频道/节目。
- 各源独立处理。单个源失败时保留有效旧文件，其他源继续更新；全部源失败时任务标记为失败。
- 旧脚本误存的 HTML 错误页等无效缓存会清除，上游恢复后自动重建。
- 每次运行的 Actions 摘要列出各源的更新、未变化或失败结果；保留的旧文件不代表上游已恢复更新。
- 同仓库的 `sync` 通知使用 Actions 自动生成的 `GITHUB_TOKEN`，无需配置 `ACCESS_TOKEN`。

新增或修改第三方源时，编辑 `files.json` 中的文件名与上游 URL 即可。支持 XML 和 GZ 上游，配置中的文件名统一以 `.xml` 结尾；配置提交后会自动运行一次更新。
