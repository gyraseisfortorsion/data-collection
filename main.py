import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


cred = credentials.Certificate('key.json')
firebase_admin.initialize_app(cred)

db = firestore.client()


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


SUPERUSER_ID = 169161947


def start(update: Update, context):
    """Send a welcome message when the command /start is issued."""
    user_id = update.message.chat_id
    if user_id == SUPERUSER_ID:

        update.message.reply_text('You are a superuser.')
    else:
        update.message.reply_text(
            'You are now connected to the superuser. Write anything to send a message to the superuser')

# Handler for incoming messages


def chat(update: Update, context):
    """Relay incoming messages to the superuser and handle superuser responses."""
    user_id = update.message.chat_id
    message_id = update.message.message_id
    message_text = update.message.text

    if user_id == SUPERUSER_ID:

        # if message_text.startswith('/reply'):
            # reply_text = message_text.replace('/reply', '').strip()
            # recipient_id, reply_message = reply_text.split(maxsplit=1)
            # context.bot.send_message(chat_id=int(
            #     recipient_id), text=reply_message)
        # else:
        #     update.message.reply_text(
        #         'You should type /reply <user_id> <message> to reply to a user.')
        if update.message.reply_to_message:
            replied_message = update.message.reply_to_message
            if replied_message.text and replied_message.text.startswith("Anonymous user ("):
                # Extract the anonymous user ID from the replied message
                start_idx = replied_message.text.index("(")
                end_idx = replied_message.text.index(")")
                anonymous_user_id = replied_message.text[start_idx + 1 : end_idx]
                context.bot.send_message(chat_id=int(anonymous_user_id), text=message_text)
            else:
                update.message.reply_text("You can only reply to an anonymous message.")
        elif message_text.startswith('/reply'):
            reply_text = message_text.replace('/reply', '').strip()
            recipient_id, reply_message = reply_text.split(maxsplit=1)
            context.bot.send_message(chat_id=int(
                recipient_id), text=reply_message)
        else:
            update.message.reply_text("You can only reply to a message.")
    else:

        context.bot.send_message(
            chat_id=SUPERUSER_ID, text=f'Anonymous user ({user_id}): {message_text}')

        doc_ref = db.collection('incoming_messages').document()
        doc_ref.set({
            'user_id': user_id,
            'message_text': message_text
        })


def main():

    updater = Updater(
        "6321435565:AAGC6mZ3-RLfHHIr2VP_r3ddSDBdudk0tuk", use_context=True)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))

    dispatcher.add_handler(MessageHandler(Filters.text, chat))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
