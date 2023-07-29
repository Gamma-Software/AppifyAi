import requests
import streamlit as st


def telegram_bot_sendtext(bot_message: str, bot_token: str, bot_chat_id: str):
    return requests.get(
        "https://api.telegram.org/bot"
        + bot_token
        + "/sendMessage?chat_id="
        + bot_chat_id
        + "&parse_mode=Markdown&text="
        + bot_message
    ).json()


if st.button("Send notification"):
    telegram_bot_sendtext(
        "Hello from my App !", "6332478474:AAGr0Ds34_9hihrysLDp452gLUcqT5i5-qc", "1234567890"
    )
