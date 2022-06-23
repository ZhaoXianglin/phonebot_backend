from google.cloud import dialogflow


def detect_intent_texts(project_id, session_id, text, language_code):
    """
    :param project_id: dialogflow 项目id
    :param session_id: 用户uuid
    :param text: 用户输入文本
    :param language_code: en
    :return:
    dict{ intent: str, entities:dict, text:str }
    """
    session_client = dialogflow.SessionsClient()

    session = session_client.session_path(project_id, session_id)
    text_input = dialogflow.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.QueryInput(text=text_input)
    response = session_client.detect_intent(
        request={'session': session, 'query_input': query_input})
    # 意图和置信度
    entities = {}
    for item in response.query_result.parameters:
        entities[item] = response.query_result.parameters[item]
    # print(entities)
    print('Detected intent: {} (confidence: {})\n'.format(
        response.query_result.intent.display_name,
        response.query_result.intent_detection_confidence))
    # 返回的答案
    print('Fulfillment text: {}\n'.format(
        response.query_result.fulfillment_text))
    return {
        'intent': response.query_result.intent.display_name,
        'entities': entities,
        'text': response.query_result.fulfillment_text}
