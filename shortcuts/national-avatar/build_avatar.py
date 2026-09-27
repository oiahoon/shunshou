"""Build the offline avatar styling Shortcut."""
import base64
from pathlib import Path
import plistlib
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from build import Workflow, attachment, uid  # noqa: E402

BASE = Path(__file__).resolve().parent
VERSION = "2.0.0"

STYLES = [
    ("经典旗帜", "overlay.png"),
    ("柔和渐变", "overlay-gradient.png"),
    ("在线 · 绿色边框", "status-online.png"),
    ("忙碌 · 金色边框", "status-busy.png"),
    ("离开 · 橙色边框", "status-away.png"),
    ("请勿打扰 · 红色边框", "status-dnd.png"),
    ("隐身 · 灰色边框", "status-invisible.png"),
]


def build():
    w = Workflow()
    w.action("comment", WFCommentActionText=(
        f"头像装扮 {VERSION}。请先在照片 App 中把头像裁成正方形，再选择照片和喜欢的样式。"
        "可选国庆旗帜或在线状态边框，捷径在本机缩放并叠加透明装饰。"
        "预览后保存到照片。原图不会修改；照片不会上传到本站或第三方。"
        "非正方形照片会被拉伸，请先裁好再运行。"
    ))
    photo = w.action("selectphoto", "Selected photo", WFSelectMultiplePhotos=False)
    sized = w.action("image.resize", "Avatar base", WFImage=photo,
                     WFImageResizeWidth=1024, WFImageResizeHeight=1024)
    menu = uid()
    w.action("choosefrommenu", WFControlFlowMode=0, GroupingIdentifier=menu,
             WFMenuPrompt="选择头像样式：国庆主题或在线状态边框。每次选择一种样式。",
             WFMenuItems=[label for label, _ in STYLES])
    for label, filename in STYLES:
        w.action("choosefrommenu", WFControlFlowMode=1, GroupingIdentifier=menu,
                 WFMenuItemTitle=label)
        encoded = base64.b64encode((BASE / filename).read_bytes()).decode("ascii")
        image_text = w.action("gettext", label + " data", WFTextActionText=encoded)
        overlay = w.action("base64encode", label + " overlay", WFInput=image_text,
                           WFEncodeMode="Decode")
        w.action("setvariable", WFVariableName="Avatar overlay", WFInput=overlay)
    w.action("choosefrommenu", WFControlFlowMode=2, GroupingIdentifier=menu)
    chosen_overlay = attachment({"Type": "Variable", "VariableName": "Avatar overlay"})
    composite = w.action("overlayimageonimage", "Styled avatar",
                         WFInput=sized, WFImage=chosen_overlay,
                         WFShouldShowImageEditor=False, WFImagePosition="Center",
                         WFImageWidth=1024, WFImageHeight=1024,
                         WFOverlayImageOpacity=100)
    w.action("previewdocument", WFInput=composite)
    w.action("savetocameraroll", WFInput=composite)
    w.action("notification", WFNotificationActionTitle="头像装扮已保存",
             WFNotificationActionBody="打开照片 App 查看并设为微信头像。",
             WFNotificationActionSound=False)
    return {
        "WFWorkflowName": "头像装扮",
        "WFWorkflowActions": w.actions,
        "WFWorkflowClientVersion": "4610",
        "WFWorkflowMinimumClientVersion": 3010,
        "WFWorkflowMinimumClientVersionString": "3010",
        "WFWorkflowIcon": {"WFWorkflowIconGlyphNumber": 59511,
                           "WFWorkflowIconStartColor": 4280023039},
        "WFWorkflowTypes": ["WFWorkflowTypeShowInSearch"],
        "WFWorkflowInputContentItemClasses": [],
        "WFWorkflowOutputContentItemClasses": ["WFImageContentItem"],
        "WFWorkflowHasShortcutInputVariables": False,
        "WFWorkflowHasOutputFallback": False,
    }


if __name__ == "__main__":
    output = BASE / "头像装扮-未签名.shortcut"
    with output.open("wb") as file:
        plistlib.dump(build(), file, fmt=plistlib.FMT_XML, sort_keys=False)
    print(output, len(build()["WFWorkflowActions"]), "actions")
