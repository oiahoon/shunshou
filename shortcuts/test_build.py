import unittest
from build import build, BASE, PLACEHOLDER


class WorkflowTests(unittest.TestCase):
    def test_match_text_binds_named_input_without_runtime_prompt(self):
        actions = build()["WFWorkflowActions"]
        match = next(a["WFWorkflowActionParameters"] for a in actions if a["WFWorkflowActionIdentifier"].endswith(".text.match"))
        self.assertNotIn("WFInput", match)
        self.assertEqual(match["text"]["WFSerializationType"], "WFTextTokenString")
        ref = match["text"]["Value"]["attachmentsByRange"]["{0, 1}"]
        self.assertEqual(ref, {"Type":"Variable", "VariableName":"Link input"})
        self.assertFalse(any(a["WFWorkflowActionIdentifier"].endswith(".ask") for a in actions))

    def test_clipboard_experiment_preserves_media_and_share_fallback(self):
        actions = build()["WFWorkflowActions"]
        by_id = {a["WFWorkflowActionParameters"]["UUID"]: a for a in actions}
        copy = next(a["WFWorkflowActionParameters"] for a in actions if a["WFWorkflowActionIdentifier"].endswith(".setclipboard"))
        self.assertTrue(copy["WFLocalOnly"])
        source = by_id[copy["WFInput"]["Value"]["OutputUUID"]]
        self.assertTrue(source["WFWorkflowActionIdentifier"].endswith(".getitemfromlist"))
        self.assertEqual(source["WFWorkflowActionParameters"]["WFItemSpecifier"], "First Item")
        expiry_ref = copy["WFExpirationDate"]["Value"]["attachmentsByRange"]["{0, 1}"]["OutputUUID"]
        expiry = by_id[expiry_ref]["WFWorkflowActionParameters"]
        now_ref = expiry["WFDate"]["Value"]["attachmentsByRange"]["{0, 1}"]["OutputUUID"]
        self.assertEqual(by_id[now_ref]["WFWorkflowActionParameters"]["WFDateActionMode"], "Current Date")
        self.assertEqual(expiry["WFDuration"]["Value"], {"Magnitude":5,"Unit":"min"})
        self.assertEqual(expiry["WFAdjustOperation"], "Add")
        menus = [a["WFWorkflowActionParameters"] for a in actions if a["WFWorkflowActionIdentifier"].endswith(".choosefrommenu")]
        self.assertEqual([p["WFControlFlowMode"] for p in menus], [0,1,1,2])
        self.assertEqual(menus[0]["WFMenuItems"], [p["WFMenuItemTitle"] for p in menus[1:3]])
        self.assertEqual(sum(a["WFWorkflowActionIdentifier"].endswith(".share") for a in actions), 1)
        self.assertEqual(next(a["WFWorkflowActionParameters"]["WFURLActionURL"] for a in actions if a["WFWorkflowActionIdentifier"].endswith(".url")), "weixin://")
        self.assertEqual(sum(a["WFWorkflowActionIdentifier"].endswith(".openurl") for a in actions), 1)

    def test_production_domain(self):
        self.assertEqual(BASE, "https://shunshou.miaowu.org")

    def test_actions_reference_existing_outputs(self):
        for workflow in (build(),):
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
        for workflow in (build(),):
            stack = []
            for action in workflow["WFWorkflowActions"]:
                p = action["WFWorkflowActionParameters"]
                mode = p.get("WFControlFlowMode")
                if mode == 0: stack.append(p["GroupingIdentifier"])
                elif mode == 2: self.assertEqual(stack.pop(), p["GroupingIdentifier"])
            self.assertFalse(stack)

    def test_import_question_configures_token(self):
        for workflow in (build(),):
            question = workflow["WFWorkflowImportQuestions"][0]
            action = workflow["WFWorkflowActions"][question["ActionIndex"]]
            self.assertEqual(action["WFWorkflowActionParameters"][question["ParameterKey"]], PLACEHOLDER)

    def test_authorization_never_sent_to_cdn(self):
        actions = build()["WFWorkflowActions"]
        requests = [a["WFWorkflowActionParameters"] for a in actions if a["WFWorkflowActionIdentifier"].endswith(".downloadurl")]
        self.assertEqual(len(requests),3)
        self.assertEqual(requests[0]["WFURL"], BASE+"/api/health")
        self.assertEqual(requests[1]["WFURL"], BASE+"/api/resolve")
        for request in requests[:2]:
            self.assertIn("Authorization", str(request))
        self.assertNotIn("Authorization",str(requests[2]))
        self.assertEqual(requests[1]["WFHTTPBodyType"],"JSON")
        self.assertNotIn("savefile",str(actions))
        self.assertNotIn("delete",str(actions))

    def test_string_conditions_have_text_inputs_and_literals(self):
        outputs = {}
        literals = []
        for action in build()["WFWorkflowActions"]:
            p = action["WFWorkflowActionParameters"]
            if "WFConditionalActionString" in p:
                ref = p["WFInput"]["Variable"]["Value"]["OutputUUID"]
                source = outputs[ref]
                self.assertEqual(source["WFWorkflowActionIdentifier"], "is.workflow.actions.gettext")
                self.assertEqual(source["WFWorkflowActionParameters"]["WFTextActionText"]["WFSerializationType"], "WFTextTokenString")
                literals.append((p["WFCondition"], p["WFConditionalActionString"]))
            if p.get("WFCondition") in (100, 101):
                self.assertNotIn("WFConditionalActionString", p)
            outputs[p["UUID"]] = action
        self.assertEqual(literals, [(4, PLACEHOLDER), (4, "ok"), (5, "ok"), (99, "NO_AUDIO")])

    def test_health_only_runs_in_missing_link_branch(self):
        actions = build()["WFWorkflowActions"]
        match_index = next(i for i, a in enumerate(actions) if a["WFWorkflowActionIdentifier"].endswith(".text.match"))
        condition = actions[match_index + 1]["WFWorkflowActionParameters"]
        self.assertEqual(condition["WFCondition"], 101)
        end = next(i for i in range(match_index + 2, len(actions))
                   if actions[i]["WFWorkflowActionParameters"].get("GroupingIdentifier") == condition["GroupingIdentifier"])
        branch = actions[match_index + 2:end]
        self.assertEqual(branch[0]["WFWorkflowActionParameters"]["WFURL"], BASE + "/api/health")
        self.assertEqual(branch[-1]["WFWorkflowActionIdentifier"], "is.workflow.actions.exit")
        self.assertEqual(sum(a["WFWorkflowActionIdentifier"].endswith(".exit") for a in branch), 2)
        self.assertNotIn("/api/resolve", str(branch))


if __name__ == "__main__": unittest.main()
