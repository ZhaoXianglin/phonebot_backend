from google.cloud import dialogflow


def detect_intent_texts(project_id, session_id, text, language_code):
    """检测输入返回意图名称"""
    session_client = dialogflow.SessionsClient()

    session = session_client.session_path(project_id, session_id)
    text_input = dialogflow.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.QueryInput(text=text_input)
    response = session_client.detect_intent(
        request={'session': session, 'query_input': query_input})
    # 意图和置信度
    print('Detected intent: {} (confidence: {})\n'.format(
        response.query_result.intent.display_name,
        response.query_result.intent_detection_confidence))
    # 返回的答案
    print('Fulfillment text: {}\n'.format(
        response.query_result.fulfillment_text))
    return response.query_result.intent.display_name, response.query_result.fulfillment_text