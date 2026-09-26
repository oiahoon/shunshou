"""Build a portable, token-free business expense Shortcut."""
from pathlib import Path
import plistlib
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from build import Workflow, attachment, text, uid  # noqa: E402

VERSION = "1.0.0"
FILENAME = "BusinessTripExpenses.csv"
BASE = Path(__file__).resolve().parent


def variable(name):
    return attachment({"Type": "Variable", "VariableName": name})


def remember(w, name, value):
    w.action("setvariable", WFVariableName=name, WFInput=value)
    return variable(name)


def csv_text(w, value, name):
    # RFC 4180 quoting: doubled inner quotes, surrounding quotes. This also
    # preserves commas and line breaks in notes when opened by Numbers.
    escaped = w.action("text.replace", name + " escaped", WFInput=text(value),
                       WFReplaceTextFind='"', WFReplaceTextReplace='""',
                       WFReplaceTextCaseSensitive=True)
    return w.action("gettext", name + " CSV", WFTextActionText=text('"', escaped, '"'))


def build():
    w = Workflow()
    w.action("comment", WFCommentActionText=(
        f"出差开销 {VERSION}。每位使用者把记录保存在自己的 iCloud Drive／Shortcuts／{FILENAME}。"
        "首次运行会创建文件；以后追加一行。不会上传到作者的服务器。"
        "旧版 Documents／BusinessExpenses.csv 不会自动迁移，请自行备份和合并。"
        "城市手动填写，避免定位权限或定位服务不可用阻止记录。金额需大于零。"
    ))
    currency_index = len(w.actions)
    currency = w.action("gettext", "Currency", WFTextActionText="CNY")
    amount = w.action("ask", "Amount", WFInputType="Number",
                      WFAskActionAllowsNegativeNumbers=False,
                      WFAskActionPrompt="金额（大于 0）")
    invalid = uid()
    w.action("conditional", WFInput={"Type": "Variable", "Variable": amount},
             WFCondition=1, WFNumberValue="0",
             WFControlFlowMode=0, GroupingIdentifier=invalid)
    w.alert("金额无效", "请输入大于 0 的金额，未写入记录。")
    w.action("exit")
    w.end(invalid)
    categories = w.action("list", "Categories", WFItems=["餐饮", "交通", "住宿", "办公", "其他"])
    category = w.action("choosefromlist", "Category", WFInput=categories,
                        WFChooseFromListActionPrompt="选择开销类别",
                        WFChooseFromListActionSelectMultiple=False)
    city = w.action("ask", "City", WFInputType="Text", WFAllowsMultilineText=False,
                    WFAskActionPrompt="城市（可留空）")
    note = w.action("ask", "Note", WFInputType="Text", WFAllowsMultilineText=False,
                    WFAskActionPrompt="用途或备注（可留空）")
    now = w.action("date", "Captured time", WFDateActionMode="Current Date")
    date = w.action("gettext", "Date", WFTextActionText=text(attachment({
        **now["Value"], "Aggrandizements": [{"Type": "WFDateFormatVariableAggrandizement",
        "WFDateFormatStyle": "Custom", "WFDateFormat": "yyyy-MM-dd",
        "WFISO8601IncludeTime": False}]})))
    time = w.action("gettext", "Time", WFTextActionText=text(attachment({
        **now["Value"], "Aggrandizements": [{"Type": "WFDateFormatVariableAggrandizement",
        "WFDateFormatStyle": "Custom", "WFDateFormat": "HH:mm:ss",
        "WFISO8601IncludeTime": False}]})))
    city_csv = csv_text(w, city, "City")
    note_csv = csv_text(w, note, "Note")
    row = w.action("gettext", "CSV row", WFTextActionText=text(
        date, ",", time, ",", city_csv, ",", amount, ",", currency,
        ",", category, ",", note_csv))
    existing = w.action("documentpicker.open", "Expense file",
                        WFGetFilePath=FILENAME, WFFileErrorIfNotFound=False)
    missing = w.condition(existing, 101)
    first = w.action("gettext", "CSV with header", WFTextActionText=text(
        "Date,Time,City,Amount,Currency,Category,Purpose\n", row))
    named = w.action("setitemname", "Named CSV", WFInput=first, WFName=FILENAME)
    saved = w.action("documentpicker.save", "Saved CSV", WFInput=named,
                     WFAskWhereToSave=False, WFFileDestinationPath=FILENAME,
                     WFSaveFileOverwrite=False)
    w.action("conditional", WFControlFlowMode=1, GroupingIdentifier=missing)
    appended = w.action("file.append", "Appended CSV", WFInput=text(row),
                        WFFilePath=FILENAME, WFAppendOnNewLine=True)
    w.end(missing)
    w.action("notification", WFNotificationActionTitle="出差开销已记录",
             WFNotificationActionBody=text(amount, " ", currency, " · ", category),
             WFNotificationActionSound=False)
    return {
        "WFWorkflowName": "出差开销",
        "WFWorkflowActions": w.actions,
        "WFWorkflowClientVersion": "4610",
        "WFWorkflowMinimumClientVersion": 3010,
        "WFWorkflowMinimumClientVersionString": "3010",
        "WFWorkflowIcon": {"WFWorkflowIconGlyphNumber": 61440,
                           "WFWorkflowIconStartColor": 4292093695},
        "WFWorkflowTypes": ["WFWorkflowTypeShowInSearch"],
        "WFWorkflowInputContentItemClasses": [],
        "WFWorkflowOutputContentItemClasses": [],
        "WFWorkflowHasShortcutInputVariables": False,
        "WFWorkflowHasOutputFallback": False,
        "WFWorkflowImportQuestions": [{
            "ActionIndex": currency_index, "Category": "Parameter",
            "ParameterKey": "WFTextActionText",
            "Text": "默认币种代码（例如 CNY、USD、EUR）。以后也可以编辑顶部文本动作修改。",
            "DefaultValue": "CNY",
        }],
    }


if __name__ == "__main__":
    output = BASE / "出差开销-未签名.shortcut"
    with output.open("wb") as file:
        plistlib.dump(build(), file, fmt=plistlib.FMT_XML, sort_keys=False)
    print(output, len(build()["WFWorkflowActions"]), "actions")
