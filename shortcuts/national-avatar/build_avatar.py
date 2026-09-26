"""Build the offline National Day avatar Shortcut."""
import base64
from pathlib import Path
import plistlib
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from build import Workflow, attachment, text, uid  # noqa: E402

BASE = Path(__file__).resolve().parent
VERSION = "1.1.1"

STYLES = [
    ("经典旗帜", "overlay.png"),
    ("柔和渐变", "overlay-gradient.png"),
    ("渐变 · 国庆在线", "overlay-gradient-status.png"),
]


def build():
    w = Workflow()
    w.action("comment", WFCommentActionText=(
        f"国庆头像 {VERSION}。选择一张照片和三种样式之一，在本机居中裁成方形并叠加五星红旗主题装饰。"
        "预览后保存到照片。原图不会修改；照片不会上传到本站或第三方。"
        "请在预览里检查裁切是否合适；如人物不在中央，先用照片 App 调整原图。"
    ))
    photo = w.action("selectphoto", "Selected photo", WFSelectMultiplePhotos=False)
    width = w.action("properties.images", "Photo width", WFInput=photo,
                     WFContentItemPropertyName="Width")
    height = w.action("properties.images", "Photo height", WFInput=photo,
                      WFContentItemPropertyName="Height")
    dimensions = w.action("list", "Dimensions", WFItems=[
        {"WFItemType": 0, "WFValue": text(width)},
        {"WFItemType": 0, "WFValue": text(height)},
    ])
    side = w.action("statistics", "Shorter side", WFInput=dimensions,
                    WFStatisticsOperation="Minimum")
    square = w.action("image.crop", "Square photo", WFInput=photo,
                      WFImageCropPosition="Center", WFImageCropWidth=side,
                      WFImageCropHeight=side)
    sized = w.action("image.resize", "Avatar base", WFImage=square,
                     WFImageResizeWidth=1024, WFImageResizeHeight=1024)
    menu = uid()
    w.action("choosefrommenu", WFControlFlowMode=0, GroupingIdentifier=menu,
             WFMenuPrompt="选择头像样式。渐变款会向照片中央自然淡出；「国庆在线」另加右下角状态标记。",
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
    composite = w.action("overlayimageonimage", "National Day avatar",
                         WFInput=sized, WFImage=chosen_overlay,
                         WFShouldShowImageEditor=False, WFImagePosition="Center",
                         WFImageWidth=1024, WFImageHeight=1024,
                         WFOverlayImageOpacity=100)
    png = w.action("image.convert", "Final PNG", WFInput=composite,
                   WFImageFormat="PNG", WFImagePreserveMetadata=False)
    w.action("previewdocument", WFInput=png)
    w.action("savetocameraroll", WFInput=png)
    w.action("notification", WFNotificationActionTitle="国庆头像已保存",
             WFNotificationActionBody="打开照片 App 查看并设为微信头像。",
             WFNotificationActionSound=False)
    return {
        "WFWorkflowName": "国庆头像",
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
    output = BASE / "国庆头像-未签名.shortcut"
    with output.open("wb") as file:
        plistlib.dump(build(), file, fmt=plistlib.FMT_XML, sort_keys=False)
    print(output, len(build()["WFWorkflowActions"]), "actions")
