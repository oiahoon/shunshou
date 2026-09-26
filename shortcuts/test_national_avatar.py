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
        self.assertEqual(ids, ["comment", "selectphoto", "properties.images", "properties.images",
                               "list", "statistics", "image.crop", "image.resize", "gettext",
                               "base64encode", "overlayimageonimage", "image.convert",
                               "previewdocument", "savetocameraroll", "notification"])
        self.assertEqual(actions[5]["WFWorkflowActionParameters"]["WFStatisticsOperation"], "Minimum")
        self.assertEqual(actions[10]["WFWorkflowActionParameters"]["WFImagePosition"], "Center")
        self.assertFalse(actions[10]["WFWorkflowActionParameters"]["WFShouldShowImageEditor"])
        self.assertFalse(actions[11]["WFWorkflowActionParameters"]["WFImagePreserveMetadata"])
        self.assertNotIn("downloadurl", ids)
        self.assertNotIn("url", ids)
        self.assertTrue((SOURCE.parent / "overlay.png").read_bytes().startswith(b"\x89PNG\r\n\x1a\n"))
        self.assertEqual((SOURCE.parent / "国庆头像.shortcut").read_bytes(),
                         (SOURCE.parents[2] / "services/resolver/public/national-avatar.shortcut").read_bytes())


if __name__ == "__main__":
    unittest.main()
