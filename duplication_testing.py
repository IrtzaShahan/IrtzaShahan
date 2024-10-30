import logging
import json
import os
import sqlite3
from datetime import datetime

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Updater, MessageHandler, Filters, CallbackContext,
    CallbackQueryHandler, CommandHandler
)

DB_NAME = 'tobedo.sqlite3'

CHECK_CHAR = '✅'
UNCHECK_CHAR = '⬜'

def gen_db():
    with sqlite3.connect(DB_NAME) as db:
        db.execute('''
            CREATE TABLE IF NOT EXISTS Replies (
                message_and_chat_id VARCHAR(255) NOT NULL,
                reply_and_chat_id VARCHAR(255) NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                state TEXT,
                PRIMARY KEY (message_and_chat_id),
                UNIQUE (reply_and_chat_id)
            )
        ''')
        db.commit()

def cleanup_old_replies():
    with sqlite3.connect(DB_NAME) as db:
        db.execute('''
            DELETE FROM Replies WHERE created_at < datetime('now', '-1 year')
        ''')
        db.commit()

def get_reply_by_message_id(message_id, chat_id) -> tuple:
    with sqlite3.connect(DB_NAME) as db:
        cursor = db.execute('''
            SELECT reply_and_chat_id, state FROM Replies WHERE message_and_chat_id = ?
        ''', (f"{chat_id}_{message_id}",))
        row = cursor.fetchone()
        if not row:
            return None, None
        return row[0], json.loads(row[1]) if row[1] else {}

def insert_reply(message_id, reply_id, chat_id, state):
    with sqlite3.connect(DB_NAME) as db:
        db.execute(
            '''
            INSERT INTO Replies (message_and_chat_id, reply_and_chat_id, state) VALUES (?, ?, ?)
            ''',
            (f"{chat_id}_{message_id}", f"{chat_id}_{reply_id}", json.dumps(state))
        )
        db.commit()

def update_reply(reply_id, chat_id, state: dict):
    with sqlite3.connect(DB_NAME) as db:
        db.execute('''
            UPDATE Replies SET state = ? WHERE reply_and_chat_id = ?
        ''',
        (json.dumps(state), f"{chat_id}_{reply_id}"))
        db.commit()

logger = logging.getLogger(__name__)

TOKEN = "7412810965:AAH7Fp4vcCP7X9PpkD23dVB7eq59cLzRE9k"

def button_click(update, context):
    query = update.callback_query
    reply_message = query.message
    reply_id = reply_message.message_id
    chat_id = reply_message.chat_id

    with sqlite3.connect(DB_NAME) as db:
        cursor = db.execute('''
            SELECT message_and_chat_id, state FROM Replies WHERE reply_and_chat_id = ?
        ''', (f"{chat_id}_{reply_id}",))
        row = cursor.fetchone()
        if not row:
            print(f'No original message found for reply_id {reply_id} and chat_id {chat_id}')
            return
        message_and_chat_id, state = row[0], json.loads(row[1]) if row[1] else {}

    data = query.data
    if data.startswith('toggle__'):
        index = int(data.replace('toggle__', ''))
        steps = state['steps']
        if index < 0 or index >= len(steps):
            print(f'Invalid index {index} for steps')
            return
        step_info = steps[index]
        checked = step_info['checked']

        # Toggle the step
        if not checked:
            # Mark as checked
            step_info['checked'] = True
            step_info['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M')
        else:
            # Uncheck the step
            step_info['checked'] = False
            step_info['timestamp'] = None

        # Update the state in the database
        update_reply(reply_id, chat_id, state)

        # Update the message text to include timestamps
        title = state.get('title', 'Checklist')
        message_text = f'{title}\n'
        keyboard = []
        for idx, step in enumerate(steps):
            btn_text = f"{CHECK_CHAR if step['checked'] else UNCHECK_CHAR} {step['text']}"
            keyboard.append([InlineKeyboardButton(
                btn_text,
                callback_data=f"toggle__{idx}"
            )])
            if step['checked'] and step['timestamp']:
                message_text += f"{step['text']} - {step['timestamp']}\n"
            else:
                message_text += f"{step['text']}\n"

        reply_markup = InlineKeyboardMarkup(keyboard)

        # Edit the message text and reply markup
        context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=reply_id,
            text=message_text,
            reply_markup=reply_markup
        )

        # Send a notification if prior steps are incomplete
        prior_incomplete = False
        for prior_step in steps[:index]:
            if not prior_step['checked']:
                prior_incomplete = True
                break
        if prior_incomplete:
            context.bot.answer_callback_query(
                callback_query_id=query.id,
                text='An earlier step has not been completed yet. Please check on it.',
                show_alert=True
            )

        # Send a message upon completion of a step
        prior_completion_message_id = state.get('completion_message_id')

        # Send new completion message
        completion_status = CHECK_CHAR if step_info['checked'] else UNCHECK_CHAR
        completion_text = f"{title}: {step_info['text']} {completion_status}"
        completion_message = context.bot.send_message(
            chat_id=chat_id,
            text=completion_text
        )

        # Delete prior completion message if exists
        if prior_completion_message_id:
            try:
                context.bot.delete_message(
                    chat_id=chat_id,
                    message_id=prior_completion_message_id
                )
            except:
                pass  # Ignore errors if message was already deleted

        # Update the completion message ID in the state
        state['completion_message_id'] = completion_message.message_id

        # Update the state in the database
        update_reply(reply_id, chat_id, state)

def checklist_handler(update: Update, context: CallbackContext) -> None:
    msg = None
    update_object = None

    if update.message:
        msg = update.message.text
        update_object = update.message
    elif update.edited_message:
        msg = update.edited_message.text
        update_object = update.edited_message
    else:
        print('Unrecognized update')
        return

    if not msg:
        print('Message has no text')
        return

    # Remove '/checklist' command from message
    if msg.startswith('/checklist'):
        msg_without_command = msg.partition(' ')[2]
    else:
        msg_without_command = msg

    if not msg_without_command:
        update_object.reply_text('Please provide the checklist items after the /checklist command.')
        return

    lines = msg_without_command.strip().split('\n')

    if not lines:
        update_object.reply_text('Please provide the checklist items after the /checklist command.')
        return

    title = lines[0].strip()
    steps = lines[1:]

    # Retrieve previous state if any
    message_id = update_object.message_id
    chat_id = update_object.chat_id
    reply_id_with_message_id, previous_state = get_reply_by_message_id(message_id, chat_id)

    state = {
        'title': title,
        'completion_message_id': previous_state.get('completion_message_id') if previous_state else None,
        'steps': []
    }

    keyboard = []
    for index, step in enumerate(steps):
        step = step.strip()
        if step == '':
            continue
        # Try to preserve the checked status if the step text matches
        if previous_state:
            existing_step = next((s for s in previous_state['steps'] if s['text'] == step), None)
            if existing_step:
                checked = existing_step['checked']
                timestamp = existing_step['timestamp']
            else:
                checked = False
                timestamp = None
        else:
            checked = False
            timestamp = None
        state['steps'].append({'text': step, 'checked': checked, 'timestamp': timestamp})
        btn_text = f"{CHECK_CHAR if checked else UNCHECK_CHAR} {step}"
        keyboard.append([InlineKeyboardButton(
            btn_text,
            callback_data=f"toggle__{index}"
        )])

    reply_markup = InlineKeyboardMarkup(keyboard)

    # Construct the message text
    message_text = f"{title}\n"
    for step_info in state['steps']:
        if step_info['checked'] and step_info['timestamp']:
            message_text += f"{step_info['text']} - {step_info['timestamp']}\n"
        else:
            message_text += f"{step_info['text']}\n"

    if previous_state:
        # Update the existing checklist message
        reply_id = reply_id_with_message_id.split('_')[1]
        context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=int(reply_id),
            text=message_text,
            reply_markup=reply_markup
        )
        # Update the state in the database
        update_reply(int(reply_id), chat_id, state)
    else:
        # Send new checklist message
        reply = update_object.reply_text(message_text, reply_markup=reply_markup)
        reply_id = reply.message_id
        insert_reply(message_id, reply_id, chat_id, state)

def main() -> None:
    gen_db()
    cleanup_old_replies()
    updater = Updater(TOKEN)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('checklist', checklist_handler))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, checklist_handler))
    dispatcher.add_handler(CallbackQueryHandler(button_click))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
