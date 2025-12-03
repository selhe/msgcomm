from flask import jsonify
from datetime import datetime
from flask_socketio import emit, join_room, leave_room
from flask import request

from . import socketio, db
from .models import Conversation, Message

@socketio.on("join_conversation")
def handle_join_conversation(data):
    """Client joins a room for a specific conversation"""
    cid = data.get("conversation_id")
    if not cid:
        return
    
    room = f"conversation_{cid}"
    print('joined conversation', flush=True)
    join_room(room)
    emit("joined_conversation", {"conversation_id": cid}, room=request.sid)


@socketio.on("leave_conversation")
def handle_leave_conversation(data):
    print('left conversation', flush=True)
    cid = data.get("conversation_id")
    if not cid:
        return
    
    room = f"conversation_{cid}"
    leave_room(room)

@socketio.on("login")
def handle_login(data):
    uid = data.get("user_id")
    if not uid:
        return
    
    room = f"user_{uid}"
    print("logged in", flush=True)
    join_room(room)
    emit("logged_in", {"user_id": uid}, room=request.sid)

@socketio.on("logout")
def handle_logout(data):
    print("logged out", flush=True)
    uid = data.get("user_id")
    if not uid:
        return
    room = f"user_{uid}"
    leave_room(room)

@socketio.on("send_message")
def handle_send_message(data):

    print("message received", flush=True)

    cid = data.get("conversation_id")
    sender_id = data.get("sender_id")
    content = data.get("content", "")

    if not cid or not sender_id or content is None:
        return

    msg = Message(
        conversation_id=cid,
        sender_id=sender_id,
        content=content,
        type=data.get("type", "text"),
        status="sent"
    )

    db.session.add(msg)
    db.session.flush()

    # Update conversation metadata
    conv = Conversation.query.get(cid)
    if conv:
        conv.last_message_id = msg.id
        conv.last_message_date = datetime.utcnow()

    db.session.commit()

    last_msg_payload = {
        "id": msg.id,
        "conversation_id": cid,
        "sender_id": msg.sender_id,
        "type": msg.type,
        "content": msg.content,
        "created_at": msg.created_at.isoformat(),
        "attachments": [
            {
                "id": a.id,
                "file_url": a.file_url 
            } 
            for a in msg.attachments.all()
        ]
    }

    room = f"conversation_{cid}"
    socketio.emit("new_message", last_msg_payload, room=room)

    conv_payload = {
        "id": conv.id,
        "item_id": conv.item_id,
        "buyer_id": conv.buyer_id,
        "seller_id": conv.seller_id,
        "status": conv.status,
        "last_message": last_msg_payload,
        "last_message_date": conv.last_message_date.isoformat() if conv.last_message_date else None,
        "buyer_unread_count": conv.buyer_unread_count,
        "seller_unread_count": conv.seller_unread_count,
    }

    for uid in (conv.buyer_id, conv.seller_id):
        socketio.emit(
            "conversation_updated",
            conv_payload,
            room=f"user_{uid}"
        )

    return {"id": msg.id}