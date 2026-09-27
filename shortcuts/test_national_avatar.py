import importlib.util
from pathlib import Path
import unittest

SOURCE = Path(__file__).parent / "national-avatar" / "build_avatar.py"
spec = importlib.util.spec_from_file_location("national_avatar_builder", SOURCE)
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class NationalAvatarTests(unittest.TestCase):
    def test_local_photo_pipeline(self):
        workflow = builder.build()
        actions = workflow["WFWorkflowActions"]
        ids = [action["WFWorkflowActionIdentifier"].removeprefix("is.workflow.actions.")
               for action in actions]
        self.assertEqual(ids[:3], ["comment", "selectphoto", "image.resize"])
        self.assertEqual(ids[-4:], ["overlayimageonimage", "previewdocument",
                                    "savetocameraroll", "notification"])
        self.assertEqual(ids.count("base64encode"), len(builder.STYLES))
        self.assertEqual(ids.count("setvariable"), len(builder.STYLES))
        self.assertEqual(actions[3]["WFWorkflowActionParameters"]["WFMenuItems"],
                         [label for label, _ in builder.STYLES])
        self.assertEqual([label for label, _ in builder.STYLES[2:]],
                         ["在线", "离开", "请勿打扰", "离线"])
        self.assertEqual(actions[2]["WFWorkflowActionParameters"]["WFImage"],
                         builder.attachment({"Type": "ActionOutput",
                                             "OutputUUID": actions[1]["WFWorkflowActionParameters"]["UUID"],
                                             "OutputName": "Selected photo"}))
        self.assertNotIn("WFInput", actions[2]["WFWorkflowActionParameters"])
        self.assertEqual(actions[-4]["WFWorkflowActionParameters"]["WFImagePosition"], "Center")
        self.assertFalse(actions[-4]["WFWorkflowActionParameters"]["WFShouldShowImageEditor"])
        self.assertNotIn("statistics", ids)
        self.assertNotIn("image.crop", ids)
        self.assertNotIn("downloadurl", ids)
        self.assertNotIn("url", ids)
        for _, filename in builder.STYLES:
            self.assertTrue((SOURCE.parent / filename).read_bytes().startswith(b"\x89PNG\r\n\x1a\n"))
        for style in ("online", "away", "dnd", "offline"):
            svg = (SOURCE.parent / f"status-{style}.svg").read_text()
            self.assertNotIn("<text", svg)
            if style == "offline":
                self.assertIn('opacity=".72"', svg)
            else:
                self.assertNotIn("<rect", svg)
        self.assertEqual((SOURCE.parent / "头像装扮.shortcut").read_bytes(),
                         (SOURCE.parents[2] / "services/resolver/public/national-avatar.shortcut").read_bytes())


if __name__ == "__main__":
    unittest.main()
