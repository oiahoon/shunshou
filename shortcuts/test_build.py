import unittest
from build import build, BASE, PLACEHOLDER


class WorkflowTests(unittest.TestCase):
    def test_actions_reference_existing_outputs(self):
        for diagnostic in (False, True):
            workflow = build(diagnostic)
            seen = set()
            def walk(value):
                if isinstance(value, dict):
                    if value.get("Type") == "ActionOutput":
                        self.assertIn(value["OutputUUID"], seen)
                    if value.get("WFSerializationType") == "WFTextTokenString":
                        body = value["Value"]
                        encoded = body["string"].encode("utf-16-le")
                        for key in body.get("attachmentsByRange", {}):
                            offset, length = map(int, key.strip("{}").split(","))
                            self.assertEqual(length, 1)
                            self.assertEqual(encoded[offset*2:offset*2+2], "\ufffc".encode("utf-16-le"))
                    for item in value.values(): walk(item)
                elif isinstance(value,list):
                    for item in value: walk(item)
            for action in workflow["WFWorkflowActions"]:
                parameters = action["WFWorkflowActionParameters"]
                walk(parameters)
                seen.add(parameters["UUID"])

    def test_control_flow_is_balanced(self):
        for diagnostic in (False, True):
            stack = []
            for action in build(diagnostic)["WFWorkflowActions"]:
                p = action["WFWorkflowActionParameters"]
                mode = p.get("WFControlFlowMode")
                if mode == 0: stack.append(p["GroupingIdentifier"])
                elif mode == 2: self.assertEqual(stack.pop(), p["GroupingIdentifier"])
            self.assertFalse(stack)

    def test_import_question_configures_token(self):
        for diagnostic in (False, True):
            workflow = build(diagnostic)
            question = workflow["WFWorkflowImportQuestions"][0]
            action = workflow["WFWorkflowActions"][question["ActionIndex"]]
            self.assertEqual(action["WFWorkflowActionParameters"][question["ParameterKey"]], PLACEHOLDER)

    def test_authorization_never_sent_to_cdn(self):
        actions = build()["WFWorkflowActions"]
        requests = [a["WFWorkflowActionParameters"] for a in actions if a["WFWorkflowActionIdentifier"].endswith(".downloadurl")]
        self.assertEqual(len(requests),2)
        self.assertEqual(requests[0]["WFURL"], BASE+"/api/resolve")
        self.assertNotIn("Authorization",str(requests[1]))
        self.assertEqual(requests[0]["WFHTTPBodyType"],"JSON")
        self.assertNotIn("savefile",str(actions))
        self.assertNotIn("delete",str(actions))


if __name__ == "__main__": unittest.main()
