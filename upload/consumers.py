from channels import Group
from channels.auth import channel_session_user, channel_session_user_from_http


# Connected to websocket.connect
@channel_session_user_from_http
def ws_add(message):
    # Add them to the right group
    Group(f'upload-{message.user.id}').add(message.reply_channel)


# Connected to websocket.receive
@channel_session_user
def ws_message(message):
    Group(f'upload-{message.user.id}').send({
        "text": f"{message['text']}@{message.user.id}",
    })


# Connected to websocket.disconnect
@channel_session_user
def ws_disconnect(message):
    Group(f'upload-{message.user.id}').discard(message.reply_channel)
