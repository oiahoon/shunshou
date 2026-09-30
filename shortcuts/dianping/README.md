# 大众点评快写

此目录集中保存大众点评捷径的来源和发布文件：

- `大众点评-原版-未签名.shortcut`：保留的原始工作流，供追溯。
- `improve_dianping.py`：把原版收敛为当前图文工作流的构建脚本。
- `大众点评快写-优化版-未签名.shortcut`：构建结果，供检查与签名。
- `大众点评快写-优化版.shortcut`：已由 Apple Shortcuts 签名的安装文件。

发布副本在 `services/resolver/public/dianping.shortcut`；页面在同目录的 `dianping.html`，共用 `assets/hub.css`。更新时在本目录运行 `python3 improve_dianping.py`，检查工作流和导入问题，使用 `shortcuts sign --mode anyone --input 大众点评快写-优化版-未签名.shortcut --output 大众点评快写-优化版.shortcut` 签名，然后复制到发布副本，并更新页面日期及验收记录。

捷径在导入时要求用户自己的 DeepSeek API Key。请勿把填入真实 Key 的个性化捷径提交到仓库。运行时，iPhone 直接向 `api.deepseek.com` 发送商家分享信息、用户输入的体验及可选照片，生成草稿并复制到剪贴板；不会自动发布大众点评。签名和结构检查不代表 iPhone 上的运行结果已经验证。

## 1.1.0（2026-10-01）

- 保留文字入口，可选择最多 6 张照片。选择前说明照片会发送给 DeepSeek；超过 6 张提示并退出。
- iPhone 原生缩放至 1280 像素宽、转换 JPEG、关闭保留元数据，再以无换行 Base64 随文字发给 `deepseek-flash`。不经本站，不使用 Files API 持久上传。
- 图片只补充可见细节，不推断口味、服务或消费经历；文字为空时只生成客观照片记录。预览后复制，空响应退出而不覆盖剪贴板。
- 商家信息及体验通过原生字典转为 JSON，以保留引号、换行等字符；图文数组通过原始 JSON 请求体发送，避免被转成字符串。
- 大众点评版本来自 `shortcuts/build.py` 的 `DIANPING_VERSION`，同步到公开 manifest 的 `shortcuts.dianping` 与首页/详情页。顶层 manifest 版本仍属于顺手，避免提示无关的 Instagram 捷径升级。
- 仍需 iPhone 验收：纯文字、1 张/6 张照片、超过 6 张、HEIC 转换、照片权限、DeepSeek 返回与预览复制；签名和结构测试不代表实机完成。

官方图文请求格式：https://api-docs.deepseek.com/guides/vision/
