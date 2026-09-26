# 大众点评快写

此目录集中保存大众点评捷径的来源和发布文件：

- `大众点评-原版-未签名.shortcut`：保留的原始工作流，供追溯。
- `improve_dianping.py`：把原版收敛为当前 21 个动作的构建脚本。
- `大众点评快写-优化版-未签名.shortcut`：构建结果，供检查与签名。
- `大众点评快写-优化版.shortcut`：已由 Apple Shortcuts 签名的安装文件。

发布副本在 `services/resolver/public/dianping.shortcut`；页面在同目录的 `dianping.html`，共用 `assets/hub.css`。更新时在本目录运行 `python3 improve_dianping.py`，检查工作流和导入问题，使用 `shortcuts sign --mode anyone --input 大众点评快写-优化版-未签名.shortcut --output 大众点评快写-优化版.shortcut` 签名，然后复制到发布副本，并更新页面日期及验收记录。

捷径在导入时要求用户自己的 DeepSeek API Key。请勿把填入真实 Key 的个性化捷径提交到仓库。运行时，iPhone 直接向 `api.deepseek.com` 发送商家分享信息及用户输入的体验，生成草稿并复制到剪贴板；不会自动发布大众点评。签名和结构检查不代表 iPhone 上的运行结果已经验证。
