from channels import Group
from channels.auth import channel_session_user, channel_session_user_from_http


# Connected to websocket.connect
@channel_session_user_from_http
def ws_add(message):
    # confirm connection
    message.reply_channel.send({
        "accept": True,
    })

    # Add consumer to the right group
    # print(f'added WS#{message.reply_channel} to upload-{message.user.id}')
    Group(f'upload-{message.user.id}').add(message.reply_channel)


# Connected to websocket.receive
@channel_session_user
def ws_message(message):
    # print(f'got message to upload-{message.user.id}')
    Group(f'upload-{message.user.id}').send({
        "text": f"{message['text']}@{message.user.id}",
    })


# Connected to websocket.disconnect
@channel_session_user
def ws_disconnect(message):
    # print(f'removed WS#{message.reply_channel} from upload-{message.user.id}')
    Group(f'upload-{message.user.id}').discard(message.reply_channel)
