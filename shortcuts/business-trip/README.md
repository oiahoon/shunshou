# 出差开销

`build_business_trip.py` 生成原生 Apple 快捷指令定义；`出差开销-未签名.shortcut` 是可审查的 plist，`出差开销.shortcut` 是使用 `shortcuts sign --mode anyone` 签名的公开安装包。发布副本为 `services/resolver/public/business-trip.shortcut`，详情页为 `/shortcuts/business-trip`。

导入时设置默认币种代码，默认 CNY。每次运行输入大于零的金额，选择类别，并填写可留空的城市与用途。城市手动输入，避免定位授权或网络状态阻止记账。捷径使用一次当前时间生成日期和时间。

记录存于使用者自己的 `iCloud Drive/Shortcuts/BusinessTripExpenses.csv`。首次运行创建含表头的文件，以后追加。文本字段按 CSV 规则加引号并将内含的引号加倍；逗号和换行保留。实际 iOS 写入行为仍需设备验证。

旧版 `iCloud Drive/Documents/BusinessExpenses.csv` 不会自动迁移或覆盖。建议先备份，再用 Numbers 核对并手动合并。不要公开分享含开销、城市和用途的 CSV。

## 发布

```sh
python3 shortcuts/business-trip/build_business_trip.py
python3 -m unittest discover -s shortcuts -p 'test_*.py'
shortcuts sign --mode anyone --input shortcuts/business-trip/出差开销-未签名.shortcut --output shortcuts/business-trip/出差开销.shortcut
cp shortcuts/business-trip/出差开销.shortcut services/resolver/public/business-trip.shortcut
```

同时更新首页、详情页、云端验收脚本和日期。签名证明格式可导入，不证明 iPhone 已允许 iCloud Drive、CSV 已成功写入或 Numbers 已正确解析。
