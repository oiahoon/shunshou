# 顺手实验室站点结构

生产服务仍由 `services/resolver` 的 FastAPI 提供，仓库内统一管理站点和三个捷径。

| 路径 | 用途 |
| --- | --- |
| `services/resolver/public/index.html` | 捷径中心首页，目录及更新入口 |
| `services/resolver/public/insta-share.html` | Insta Share / 顺手详情、安装与更新 |
| `services/resolver/public/dianping.html` | 大众点评快写详情、安装与更新 |
| `services/resolver/public/business-trip.html` | 出差开销详情、安装与旧记录迁移说明 |
| `services/resolver/public/assets/hub.css` | 新站共享样式 |
| `services/resolver/public/assets/hub-hero.jpg` | 首页视觉素材 |
| `shortcuts/build.py`、`shortcuts/build/` | Insta Share 源码、生成与签名文件 |
| `shortcuts/dianping/` | 大众点评原版、构建脚本、未签名与签名文件 |
| `shortcuts/business-trip/` | 出差开销构建脚本、未签名与签名文件 |
| `services/resolver/public/*.shortcut` | 公开下载副本 |

公开路径为 `/`、`/shortcuts/insta-share`、`/shortcuts/dianping`、`/shortcuts/business-trip`。现有 `/shunshou.shortcut`、`/shunshou-check.shortcut`、`/release.json` 和 `/#update` 保持稳定；后者在首页指向更新中心。大众点评公开安装地址是 `/dianping.shortcut`，出差开销是 `/business-trip.shortcut`。

新增捷径时，应为它建立 `shortcuts/<slug>/` 管理源文件和签名包，在 `public` 增加详情页和公开安装副本，并把路线、首页条目、版本／更新说明和浏览器验收一起更新。不要把任何个人访问码或 API Key 放进发布文件。
