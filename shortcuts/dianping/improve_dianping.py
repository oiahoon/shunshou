import copy
import plistlib
from pathlib import Path

BASE = Path(__file__).resolve().parent
SOURCE = BASE / '大众点评-原版-未签名.shortcut'
OUTPUT = BASE / '大众点评快写-优化版-未签名.shortcut'

workflow = plistlib.loads(SOURCE.read_bytes())
original = workflow['WFWorkflowActions']
# Keep the share-sheet/clipboard fallback, one input, the request, and copying.
indices = [3, 4, 8, 9, 10, 11, 12, 23, 24, 25, 26, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41]
actions = [copy.deepcopy(original[i - 1]) for i in indices]
workflow['WFWorkflowActions'] = actions

def params(old_index):
    return actions[indices.index(old_index)]['WFWorkflowActionParameters']

def token_text(value, variables):
    attachments = {}
    position = 0
    for name in variables:
        position = value.index('￼', position)
        attachments[f'{{{position}, 1}}'] = {'VariableName': name, 'Type': 'Variable'}
        position += 1
    return {'WFSerializationType': 'WFTextTokenString',
            'Value': {'string': value, 'attachmentsByRange': attachments}}

params(11)['WFAskActionPrompt'] = '说说真实体验：点了什么、最有印象的一处细节、优缺点；价格/排队可选。随口说即可'
params(11)['WFInputType'] = 'Text'
params(4)['WFVariableName'] = 'Share text'
params(12)['WFVariableName'] = 'My notes'

system_prompt = '''你是帮我整理真实消费体验的大众点评写作助手。只输出可直接粘贴的中文点评正文，不要标题、解释或标签。
写得像认真回忆一次到店体验：从我提供的最鲜明细节切入，具体说出我喜欢或不喜欢的原因，再自然给出适合谁、是否值得推荐的判断。语气口语化、克制，有个人感受；允许一点不完美，不用固定开头结尾，不写广告话术。
我提供的亲身体验是唯一的主观事实来源。商家分享信息只用于店名、地址、品类等客观识别；不能由评分、人均或店铺类型推断口味、环境、服务、价格体验。不要补出我没说的菜品、感官细节、排队、优惠、消费金额或同行者。若我表达含糊，用原本的模糊程度，不替我编具体情节。
有足够素材时写约120–200字；素材少就写短些，不凑字数，不重复观点。优先保留具体细节，少用“整体来说”“值得打卡”“下次还会来”等套话。'''
params(23)['WFTextActionText'] = system_prompt

user_prompt = '商家分享信息（仅识别商家）：\n￼\n\n我的亲身体验（点评事实来源）：\n￼'
params(25)['WFTextActionText'] = token_text(user_prompt, ['Share text', 'My notes'])

params(32)['WFTextActionText'] = ''
request = params(35)['WFJSONValues']['Value']['WFDictionaryFieldValueItems']
request[0]['WFValue']['Value']['string'] = 'deepseek-flash'
request[1]['WFKey']['Value']['string'] = 'temperature'
request[1]['WFValue']['Value']['string'] = '0.8'
request[3]['WFKey']['Value']['string'] = 'max_tokens'
request[3]['WFValue']['Value']['string'] = '600'
request.insert(3, {
    'WFKey': {'Value': {'string': 'reasoning_effort'}, 'WFSerializationType': 'WFTextTokenString'},
    'WFItemType': 0,
    'WFValue': {'Value': {'string': 'none'}, 'WFSerializationType': 'WFTextTokenString'},
})

workflow['WFWorkflowImportQuestions'] = [{
    'ParameterKey': 'WFTextActionText', 'Category': 'Parameter',
    'ActionIndex': indices.index(32), 'Text': '请粘贴你的 DeepSeek API Key：',
    'DefaultValue': ''
}]
OUTPUT.write_bytes(plistlib.dumps(workflow, fmt=plistlib.FMT_BINARY))
print(OUTPUT.resolve(), len(actions), 'actions')
