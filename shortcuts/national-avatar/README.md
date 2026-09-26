# 国庆头像 1.0.0

从照片图库选择一张图片后，捷径在 iPhone 上取宽高的较小值，居中裁成正方形，缩放为 1024 × 1024，叠加内置的透明五星红旗装饰图，转换为不保留元数据的 PNG，预览后保存到“照片”。它不会上传原图或合成图，也不会自动修改微信头像。自动裁切不一定适合偏离画面中央的人物。

`overlay.svg` 是可编辑的图形源；`overlay.png` 是捷径与网站使用的 1024 × 1024 透明图片。参考图只用于理解用户想要的视觉效果，没有放入安装包或网站。

## 构建与签名

```sh
magick -background none shortcuts/national-avatar/overlay.svg -depth 8 shortcuts/national-avatar/overlay.png
python3 shortcuts/national-avatar/build_avatar.py
python3 -m unittest discover -s shortcuts -p 'test_*.py'
shortcuts sign --mode anyone --input shortcuts/national-avatar/国庆头像-未签名.shortcut --output shortcuts/national-avatar/国庆头像.shortcut
cp shortcuts/national-avatar/国庆头像.shortcut services/resolver/public/national-avatar.shortcut
```

若 `shortcuts sign` 在沙盒中连已知原版文件也报“格式不正确”，使用获准的原生 macOS 环境重试；签名成功和结构测试均不等同于 iPhone 实机运行。发布页为 `/shortcuts/national-avatar`，稳定安装地址为 `/national-avatar.shortcut`。每次版本更新应同步修改这里的版本号、构建脚本与页面版本/日期，重新签名并核对公开文件哈希。

## 待实机检查

在 iPhone Safari 下载并导入；分别选正方形、横图和竖图，核对居中裁切、装饰图位置、1024 像素输出、照片权限与相册保存；最后手动在微信中选用。Mac 签名不能证明这些步骤。
