import importlib.util
from pathlib import Path
import unittest


SOURCE = Path(__file__).parent / "business-trip" / "build_business_trip.py"
spec = importlib.util.spec_from_file_location("business_trip_builder", SOURCE)
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class BusinessTripTests(unittest.TestCase):
    def setUp(self):
        self.workflow = builder.build()
        self.actions = self.workflow["WFWorkflowActions"]

    def test_portable_private_storage(self):
        raw = str(self.workflow)
        self.assertIn(builder.FILENAME, raw)
        self.assertNotIn("crossDeviceItemID", raw)
        self.assertNotIn("fileProviderDomainID", raw)
        self.assertNotIn("Documents/BusinessExpenses.csv", raw)
        self.assertFalse(any("downloadurl" in a["WFWorkflowActionIdentifier"] for a in self.actions))

    def test_creation_append_and_amount_guard(self):
        ids = [a["WFWorkflowActionIdentifier"] for a in self.actions]
        prefix = "is.workflow.actions."
        self.assertLess(ids.index(prefix + "ask"), ids.index(prefix + "conditional"))
        self.assertIn(prefix + "setitemname", ids)
        self.assertIn(prefix + "documentpicker.save", ids)
        self.assertIn(prefix + "file.append", ids)
        self.assertLess(ids.index(prefix + "documentpicker.save"), ids.index(prefix + "file.append"))
        self.assertEqual(ids[-1], prefix + "notification")
        amount_guard = self.actions[3]["WFWorkflowActionParameters"]
        self.assertEqual(amount_guard["WFNumberValue"], "0")
        self.assertEqual(amount_guard["WFCondition"], 1)

    def test_csv_fields_quote_inner_quotes(self):
        replacements = [a["WFWorkflowActionParameters"] for a in self.actions
                        if a["WFWorkflowActionIdentifier"].endswith("text.replace")]
        self.assertEqual(len(replacements), 2)
        for action in replacements:
            self.assertEqual(action["WFReplaceTextFind"], '"')
            self.assertEqual(action["WFReplaceTextReplace"], '""')
        self.assertEqual(self.workflow["WFWorkflowImportQuestions"][0]["DefaultValue"], "CNY")


if __name__ == "__main__":
    unittest.main()
