import openai
from guardrails import Guard, OnFailAction
from guardrails.hub import (
    LogicCheck,
    RestrictToTopic,
    # DetectPromptInjection
)
from flask import Flask, request
from flask_cors import CORS

guard = Guard().use_many(
    LogicCheck(
        on_fail=OnFailAction.NOOP
    ),
    RestrictToTopic(
        valid_topics=['Dungeons and Dragons', 'Roleplaying games','Roleplaying', 'High fantasy'],
        on_fail=OnFailAction.NOOP,
        zero_shot_threshold=0.5
    ),

    # UnusualPrompt(on='prompt',on_fail=OnFailAction.EXCEPTION),
    # DetectPromptInjection()
)

app = Flask(__name__)
CORS(app, origins=['*'])

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.post('/chat')
def chat():
    chat:list[dict] = request.json
    print(chat)
    last_msg = chat[-1]['content']
    user_msg_validation_result = guard.parse(last_msg)
    if user_msg_validation_result.validation_passed is False:
        return "Sorry, I can't let you cheat! Don't try to get clever by changing the topic or being tricky."
    res = guard(llm_api=openai.chat.completions.create,
                msg_history=chat)
    if res.validation_passed is False:
        return "Sorry, I can't let you cheat!"
    print(res)
    return res.validated_output