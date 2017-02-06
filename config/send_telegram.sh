#!/bin/bash
TOKEN='' #insert bot token here
chat='' #insert chat id here
curl -s -d text="$1" -d chat_id="$chat" https://api.telegram.org/bot$TOKEN/sendMessage
