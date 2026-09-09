"""Build native Shortcuts plists without embedding private access codes."""
import argparse
from pathlib import Path
import plistlib
import uuid

BASE = "https://shunshou.miaowu.org"
PLACEHOLDER = "FILL_ACCESS_CODE"


def uid():
    return str(uuid.uuid4()).upper()


def attachment(value):
    return {"Value": value, "WFSerializationType": "WFTextTokenAttachment"}


def text(*parts):
    result, ranges = "", {}
    for part in parts:
        if isinstance(part, dict):
            offset = len(result.encode("utf-16-le")) // 2
            ranges[f"{{{offset}, 1}}"] = part["Value"]
            result += "\ufffc"
        else:
            result += part
    value = {"string": result}
    if ranges:
        value["attachmentsByRange"] = ranges
    return {"Value": value, "WFSerializationType": "WFTextTokenString"}


def dictionary(entries):
    return {"Value": {"WFDictionaryFieldValueItems": [
        {"WFItemType": 0, "WFKey": text(key),
         "WFValue": value if isinstance(value, dict) else text(value)}
        for key, value in entries.items()
    ]}, "WFSerializationType": "WFDictionaryFieldValue"}


class Workflow:
    def __init__(self):
        self.actions = []

    def action(self, identifier, name="Result", **parameters):
        output = uid()
        self.actions.append({"WFWorkflowActionIdentifier": "is.workflow.actions." + identifier,
                             "WFWorkflowActionParameters": {"UUID": output, "CustomOutputName": name, **parameters}})
        return attachment({"Type":"ActionOutput", "OutputUUID":output, "OutputName":name})

    def condition(self, value, code, literal=None):
        # Dictionary values are untyped in Shortcuts; string operators need Text.
        if literal is not None:
            value = self.action("gettext", "Comparison text", WFTextActionText=text(value))
        group = uid()
        parameters = {"WFInput":{"Type":"Variable", "Variable":value}, "WFCondition":code,
                      "WFControlFlowMode":0, "GroupingIdentifier":group}
        if literal is not None:
            parameters["WFConditionalActionString"] = literal
        self.action("conditional", **parameters)
        return group

    def end(self, group):
        return self.action("conditional", WFControlFlowMode=2, GroupingIdentifier=group)

    def alert(self, title, message):
        self.action("alert", WFAlertActionTitle=title, WFAlertActionMessage=message,
                    WFAlertActionCancelButtonShown=False)

    def get(self, source, key):
        return self.action("getvalueforkey", key, WFInput=source, WFDictionaryKey=key,
                           WFGetDictionaryValueType="Value")


def build():
    w = Workflow()
    w.action("comment", WFCommentActionText="顺手 0.3：新增复制视频到微信实验模式，保留系统分享。剪贴板仅本机、5 分钟后过期；微信是否接受视频需实测。没有 Instagram 链接时检查连接。仅向固定解析域名发送访问码；下载 CDN 视频时不发送访问码。不写入相册或文件目录，临时缓存由系统管理。")
    token_index = len(w.actions)
    token = w.action("gettext", "Access code", WFTextActionText=PLACEHOLDER)
    empty = w.condition(token, 4, PLACEHOLDER)
    w.alert("尚未配置访问码", "请编辑捷径，在顶部的文本操作中填入你的个人访问码。")
    w.action("exit")
    w.end(empty)
    auth = dictionary({"Authorization":text("Bearer ", token), "Content-Type":"application/json"})
    def check_connection():
        response = w.action("downloadurl", "Health response", WFURL=BASE+"/api/health",
                            WFHTTPMethod="GET", WFHTTPHeaders=auth, ShowHeaders=False)
        data = w.action("detect.dictionary", "Response", WFInput=response)
        status = w.get(data, "status")
        ok = w.condition(status, 4, "ok")
        w.alert("服务连接正常", "未检测到 Instagram 链接。请复制帖子或 Reel 链接后再运行「顺手」，或从系统分享菜单调用。连接正常不代表视频一定能下载。")
        w.action("exit")
        w.end(ok)
        message = w.get(data,"message")
        w.alert("连接失败", text(message))
        w.action("exit")

    def share_video():
        shared = attachment({"Type":"ExtensionInput"})
        w.action("setvariable", WFVariableName="Link input", WFInput=shared)
        input_var = attachment({"Type":"Variable", "VariableName":"Link input"})
        no_input = w.condition(input_var, 101)
        clipboard = w.action("getclipboard", "Clipboard")
        w.action("setvariable", WFVariableName="Link input", WFInput=clipboard)
        w.end(no_input)
        matches = w.action("text.match", "Instagram links", WFInput=text(input_var),
            WFMatchTextPattern=r"https?://(?:(?:www|m)\.)?(?:instagram\.com|instagr\.am)/(?:reels?|p|tv)/[A-Za-z0-9_-]+/?",
            WFMatchTextCaseSensitive=False)
        missing = w.condition(matches, 101)
        check_connection()
        w.end(missing)
        link = w.action("getitemfromlist", "Instagram URL", WFInput=matches, WFItemSpecifier="First Item")
        response = w.action("downloadurl", "Resolve response", WFURL=BASE+"/api/resolve", WFHTTPMethod="POST",
                            WFHTTPHeaders=auth, WFHTTPBodyType="JSON",
                            WFJSONValues=dictionary({"url":text(link),"quality":"720p"}), ShowHeaders=False)
        data = w.action("detect.dictionary", "Response", WFInput=response)
        status = w.get(data, "status")
        failed = w.condition(status, 5, "ok")
        message = w.get(data, "message")
        code = w.get(data, "code")
        w.alert("解析失败", text(code, "\n", message, "\n请稍后重试；无需重复安装捷径。"))
        w.action("exit")
        w.end(failed)
        warnings = w.get(data, "warnings")
        warning_text = w.action("gettext", "Warnings", WFTextActionText=text(warnings))
        silent = w.condition(warning_text, 99, "NO_AUDIO")
        w.alert("视频可能没有声音", "服务返回的视频没有音轨。可以继续下载，但不会自动补充音频。")
        w.end(silent)
        items = w.get(data,"items")
        no_items = w.condition(items,101)
        w.alert("没有可下载的视频", "服务没有返回视频项目。")
        w.action("exit")
        w.end(no_items)
        group = uid()
        w.action("repeat.each", WFControlFlowMode=0, GroupingIdentifier=group, WFInput=items)
        item = attachment({"Type":"Variable", "VariableName":"Repeat Item"})
        url = w.get(item,"url")
        filename = w.get(item,"filename")
        agent = w.get(item,"downloadHeaders.User-Agent")
        media = w.action("downloadurl", "Video file", WFURL=text(url), WFHTTPMethod="GET",
                         WFHTTPHeaders=dictionary({"User-Agent":text(agent), "Referer":"https://www.instagram.com/"}), ShowHeaders=False)
        w.action("setitemname", "Named video", WFInput=media, WFName=text(filename))
        files = w.action("repeat.each", "Downloaded videos", WFControlFlowMode=2, GroupingIdentifier=group)
        menu = uid()
        choices = ["复制首个视频并打开微信（实验）", "系统分享全部视频"]
        w.action("choosefrommenu", WFControlFlowMode=0, GroupingIdentifier=menu,
                 WFMenuPrompt="选择发送方式", WFMenuItems=choices)
        w.action("choosefrommenu", WFControlFlowMode=1, GroupingIdentifier=menu,
                 WFMenuItemTitle=choices[0])
        w.alert("微信粘贴实验", "将覆盖当前剪贴板，仅复制首个视频，5 分钟后过期。进入微信聊天后长按粘贴；若不能粘贴或显示为文件，请重新运行并选系统分享。不会自动发送，也不会保存到相册。")
        first = w.action("getitemfromlist", "Clipboard video", WFInput=files, WFItemSpecifier="First Item")
        now = w.action("date", "Now", WFDateActionMode="Current Date")
        expiry = w.action("adjustdate", "Clipboard expiry", WFDate=text(now), WFAdjustOperation="Add",
                          WFDuration={"Value":{"Magnitude":5,"Unit":"min"},
                                      "WFSerializationType":"WFQuantityFieldValue"})
        w.action("setclipboard", WFInput=first, WFLocalOnly=True, WFExpirationDate=text(expiry))
        wechat = w.action("url", "WeChat", WFURLActionURL="weixin://")
        w.action("openurl", WFInput=wechat)
        w.action("choosefrommenu", WFControlFlowMode=1, GroupingIdentifier=menu,
                 WFMenuItemTitle=choices[1])
        w.action("share", WFInput=files)
        w.action("choosefrommenu", WFControlFlowMode=2, GroupingIdentifier=menu)
    share_video()
    workflow = {
        "WFWorkflowName":"顺手",
        "WFWorkflowActions":w.actions, "WFWorkflowClientVersion":"3036.0.4.2",
        "WFWorkflowMinimumClientVersion":900, "WFWorkflowMinimumClientVersionString":"900",
        "WFWorkflowIcon":{"WFWorkflowIconGlyphNumber":61440,"WFWorkflowIconStartColor":4292093695},
        "WFWorkflowTypes":["ActionExtension"],
        "WFWorkflowInputContentItemClasses":["WFURLContentItem","WFStringContentItem"],
        "WFWorkflowOutputContentItemClasses":[], "WFWorkflowHasShortcutInputVariables":True,
        "WFWorkflowHasOutputFallback":False,
        "WFWorkflowImportQuestions":[{"ActionIndex":token_index,"Category":"Parameter",
            "ParameterKey":"WFTextActionText","Text":"填入你的顺手个人访问码。不要填写 Instagram 密码，也不要分享配置后的捷径。",
            "DefaultValue":PLACEHOLDER}],
    }
    return workflow


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(Path(__file__).parent / "build"))
    args = parser.parse_args()
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    workflow = build()
    with (output / "shunshou.unsigned.shortcut").open("wb") as stream:
        plistlib.dump(workflow, stream, fmt=plistlib.FMT_XML, sort_keys=False)
    print(f"Built shunshou: {len(workflow['WFWorkflowActions'])} actions; no private access code embedded.")
