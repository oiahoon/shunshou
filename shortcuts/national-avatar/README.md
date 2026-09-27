# 头像装扮 2.0.0

原「国庆头像」升级为通用的微信头像装扮捷径。先在“照片”中把头像裁成正方形，再选择一张照片和七种装扮之一：经典旗帜、柔和渐变、在线、忙碌、离开、请勿打扰、隐身。捷径在 iPhone 本机将照片缩放到 1024 × 1024，叠加内置透明 PNG，预览后保存到“照片”。它不会上传照片，也不会读取或改变微信真实的在线状态、自动更换微信头像。非方形照片会被拉伸。

五款状态边框的 SVG 是新绘制的可编辑源文件，PNG 是捷径和页面共同使用的素材。旧「微信在线状态」仅作为功能参考，没有复制远程链接、联系人卡片或网络动作。公开页面使用用户提供的头像作示例，示例头像不进入安装包。

2.0.0 保留了 1.1.2 经过 macOS 分段验证的直接缩放、内置 Base64 解码与叠图动作链。此前自动计算尺寸及裁切会生成 0 KB 图片，故不再使用。签名和单元测试不能代替完整 iPhone 实机验收。

## 构建与签名

```sh
for name in online busy away dnd invisible; do rsvg-convert -o "shortcuts/national-avatar/status-$name.png" "shortcuts/national-avatar/status-$name.svg"; done
python3 shortcuts/national-avatar/build_avatar.py
python3 -m unittest discover -s shortcuts -p 'test_*.py'
shortcuts sign --mode anyone --input shortcuts/national-avatar/头像装扮-未签名.shortcut --output shortcuts/national-avatar/头像装扮.shortcut
cp shortcuts/national-avatar/头像装扮.shortcut services/resolver/public/avatar-studio.shortcut
cp shortcuts/national-avatar/头像装扮.shortcut services/resolver/public/national-avatar.shortcut
```

`/shortcuts/avatar-studio` 是新详情页，`/shortcuts/national-avatar` 永久跳转到它。`/avatar-studio.shortcut` 是新安装地址，`/national-avatar.shortcut` 为字节一致的旧地址兼容包。旧名称与新名称可能在 iOS 中并存，用户应按系统提示确认导入，需要时自行删除旧版；不会静默替换。版本发布需同步修改构建脚本、首页、详情页、文档与安装文件。

## 实机验收

在 iPhone Safari 下载并导入；选择一张正方形照片，至少覆盖国庆渐变与五种在线状态分支，核对合成图片非空、1024 × 1024、边框位置、预览与照片保存。macOS 原生分段验证是已有证据，完整 iPhone 流程仍须在设备上确认。
