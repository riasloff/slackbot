#!/bin/python3

import os
import openai
import logging
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk.web import WebClient

SLACK_BOT_TOKEN = (os.environ['SLACK_BOT_TOKEN'])
SLACK_APP_TOKEN = (os.environ['SLACK_APP_TOKEN'])
OPENAI_API_KEY = (os.environ['OPENAI_API_KEY'])
OPENAI_MODEL = (os.environ['OPENAI_MODEL'])

# Event API & Web API (Event API for recieve messages & Web API for post them)
app = App(token=SLACK_BOT_TOKEN)
client = WebClient(SLACK_BOT_TOKEN)
logger = logging.basicConfig(level=logging.DEBUG)

def openai_response(input):
    openai.api_key = OPENAI_API_KEY
    try:

        completion = openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            messages=input,)

        return completion["choices"][0]["message"].content

    except Exception as err:
        return f":warning: {err}"


def get_conv_replies(channel_id, thread_ts):
    if channel_id is None or thread_ts is None:
        return None

    messages = client.conversations_replies(channel=channel_id, ts=thread_ts).get("messages", [])
    return messages

def is_no_mention_thread(context, parent_message) -> bool:
    parent_message_text = parent_message.get("text", "")
    return f"<@{context.bot_user_id}>" in parent_message_text

@app.event("app_mention")
def mention_content(context, payload, logger):

    reaction = client.reactions_add(channel=context.channel_id, timestamp=payload.get("event_ts"), name="brain")

    gen_history = [{"role": "system", "content": "You are a helpful assistant."},
                    {"role": "assistant", "content": "OK"},
                    {"role": "user", "content": payload.get("text")}]

    response = openai_response(gen_history)
    gen_history.append({"role": "assistant", "content": response})

    reply = client.chat_postMessage(channel=context.channel_id, thread_ts=payload.get("event_ts"), text=response)
    reaction = client.reactions_add(channel=context.channel_id, timestamp=payload.get("event_ts"), name="white_check_mark")


@app.event("message")
def message_content(context, payload, logger):
    
    if payload.get("bot_id") is not None and payload.get("bot_id") != context.bot_id:
        return
    
    try:
        logger.debug(payload)
        brain_reaction = client.reactions_add(channel=context.channel_id, timestamp=payload.get("event_ts"), name="brain")

        thread_ts = payload.get("thread_ts")

        if thread_ts is not None:
            conv_replies = get_conv_replies(payload.get('channel'), payload.get("thread_ts"))
            replies = [{"role": "system", "content": "You are a helpful assistant."},]
            for i in conv_replies:
                conv_user = i.get("user")
                conv_bot = i.get ("bot_id")
                if conv_bot is not None:
                    replies.append({"role": "assistant", "content": i.get("text")})
                elif conv_user is not None:
                    replies.append({"role": "user", "content": i.get("text")})
                else: pass
        else:
            replies = [{"role": "system", "content": "You are a helpful assistant."},
                       {"role": "assistant", "content": "OK"},
                        {"role": "user", "content": payload.get("text")}]

         
        # Send to OpenAI API
        response = openai_response(replies)

        # Reply to thread
        reply = client.chat_postMessage(channel=context.channel_id, thread_ts=payload.get("event_ts"), text=response)  
        done_reaction = client.reactions_add(channel=context.channel_id, timestamp=payload.get("event_ts"), name="white_check_mark")

    except Exception as err:
        logger.error(err)

if __name__ == "__main__":
    SocketModeHandler(app, SLACK_APP_TOKEN).start()