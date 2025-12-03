from datetime import datetime
from . import db
from sqlalchemy import Enum

message_type_enum = Enum(
    'text', 'attachment', 'system',
    name='message_type_enum',
    native_enum=False
)

message_status_enum = Enum(
    'sent', 'delivered', 'read',
    name='message_status_enum',
    native_enum=False
)

conversation_status_enum = Enum(
    'open', 'closed', 'blocked',
    name='conversation_status_enum',
    native_enum=False
)

# ============================================================
#   CONVERSATION (Parent)
# ============================================================
class Conversation(db.Model):
    __tablename__ = "conversation"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    item_id = db.Column(
        db.Integer,
        db.ForeignKey("listing.id", ondelete="CASCADE"),
        nullable=False
    )
    buyer_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False
    )
    seller_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False
    )

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(conversation_status_enum, default='open', nullable=False)

    last_message_id = db.Column(db.Integer)
    last_message_date = db.Column(db.DateTime)

    buyer_unread_count = db.Column(db.Integer, default=0)
    seller_unread_count = db.Column(db.Integer, default=0)

    messages = db.relationship(
        "Message",
        backref="conversation",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )


# ============================================================
#   MESSAGE (Child)
# ============================================================
class Message(db.Model):
    __tablename__ = "message"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    conversation_id = db.Column(
        db.Integer,
        db.ForeignKey("conversation.id", ondelete="CASCADE"),
        nullable=False
    )

    sender_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False
    )
    type = db.Column(message_type_enum, nullable=False, default='text')
    content = db.Column(db.String(500), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(message_status_enum, default='sent', nullable=False)

    attachments = db.relationship(
        "Attachment",
        backref="message",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )


# ============================================================
#   ATTACHMENT (Child of Message)
# ============================================================
class Attachment(db.Model):
    __tablename__ = "attachment"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    message_id = db.Column(
        db.Integer,
        db.ForeignKey("message.id", ondelete="CASCADE"),
        nullable=False
    )

    file_url = db.Column(db.String(500), nullable=False)
    type = db.Column(message_type_enum, nullable=False, default="attachment")

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)

class Listing(db.Model):
    __tablename__ = "listing"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)

    author_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)

    price = db.Column(db.DECIMAL(10, 2), nullable=False)

    sell_date = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(
        db.DateTime, server_default=db.func.now(), nullable=False
    )

    updated_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        onupdate=db.func.now(),
        nullable=False
    )

    deleted_at = db.Column(db.DateTime, nullable=True)