#!/usr/bin/env python3
"""
Professional Free Fire Dance Bot
Restricted to @HRDIXXTEAAAAM group
Commands: /start and /dance only
Developer: @lliillliiilliil (H4RDIXX - 𝑪𝒀𝑳)
"""

import os
import json
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, filters
from telegram.error import BadRequest

# Bot configuration
TELEGRAM_BOT_TOKEN = '8437797339:AAHF5Mk2onTUVwvXzRmbQYqkN7-IxH1b2xQ'
ALLOWED_GROUP = '@HRDIXXTEAAAAM'  # Your group only
DEVELOPER = '@lliillliiilliil'
DEVELOPER_NAME = 'H4RDIXX - 𝑪𝒀𝑳'

# Load emotes data
try:
    with open('emotes_data.json', 'r', encoding='utf-8') as f:
        EMOTES_DATA = json.load(f)
except FileNotFoundError:
    # Default emote IDs for testing
    EMOTES_DATA = [
        {'id': '909050013', 'name': 'Dance 1'},
        {'id': '909050014', 'name': 'Dance 2'},
        {'id': '909050015', 'name': 'Dance 3'},
        {'id': '909050016', 'name': 'Dance 4'},
        {'id': '909050017', 'name': 'Dance 5'},
    ]

def is_allowed_group(update: Update) -> bool:
    """Check if message is from allowed group"""
    if not update.effective_chat:
        return False
    
    # Check by username or title
    chat = update.effective_chat
    if chat.username and chat.username.lower() == ALLOWED_GROUP[1:].lower():
        return True
    if chat.title and ALLOWED_GROUP.lower() in chat.title.lower():
        return True
    
    return False

async def delete_message_later(context: ContextTypes.DEFAULT_TYPE, chat_id: int, message_id: int, delay: int = 5):
    """Delete a message after delay"""
    await asyncio.sleep(delay)
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception:
        pass

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Welcome message - works anywhere but commands only in group"""
    user = update.effective_user
    
    welcome_text = f"""Welcome {user.first_name if user else 'User'} to H4RDIXX Dance Bot.

This bot allows you to execute dance emotes in Free Fire.

**Usage:**
`/dance team_code uid1 uid2 uid3 dance_number`

**Example:**
`/dance 12345 3852380079 3852380080 3852380081 1`

**Notes:**
- Maximum 8 UIDs per command
- Dance numbers: 1 to {len(EMOTES_DATA)}
- Bot only works in {ALLOWED_GROUP}
- Developer: {DEVELOPER} ({DEVELOPER_NAME})

**Available Dances:**
Send `/dance` with parameters only."""
    
    sent_msg = await update.message.reply_text(welcome_text, parse_mode='Markdown')
    
    # Delete messages after delay
    if is_allowed_group(update):
        await delete_message_later(context, update.effective_chat.id, update.message.message_id, 10)
        await delete_message_later(context, update.effective_chat.id, sent_msg.message_id, 10)

async def dance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle dance command with format: /dance team_code uid1 uid2... dance_number"""
    
    # Check if in allowed group
    if not is_allowed_group(update):
        error_msg = await update.message.reply_text(
            f"❌ This bot only works in {ALLOWED_GROUP}\n\n"
            f"Developer: {DEVELOPER}",
            parse_mode='Markdown'
        )
        await delete_message_later(context, update.effective_chat.id, error_msg.message_id, 10)
        return
    
    # Delete user's command message
    try:
        await update.message.delete()
    except BadRequest:
        pass
    
    # Check if we have enough arguments
    if not context.args or len(context.args) < 3:
        error_msg = await update.message.reply_text(
            "Invalid format.\n\n"
            "Usage: `/dance team_code uid1 uid2 uid3 dance_number`\n"
            "Example: `/dance 12345 3852380079 3852380080 1`",
            parse_mode='Markdown'
        )
        await delete_message_later(context, update.effective_chat.id, error_msg.message_id, 10)
        return
    
    try:
        # Parse arguments
        # Last argument is dance number
        dance_number = int(context.args[-1])
        # First argument is team code
        team_code = context.args[0]
        # Everything between are UIDs
        uids = context.args[1:-1]
        
        # Validate dance number
        if dance_number < 1 or dance_number > len(EMOTES_DATA):
            error_msg = await update.message.reply_text(
                f"Dance number must be between 1 and {len(EMOTES_DATA)}",
                parse_mode='Markdown'
            )
            await delete_message_later(context, update.effective_chat.id, error_msg.message_id, 10)
            return
        
        # Validate UIDs (max 8)
        if len(uids) > 8:
            error_msg = await update.message.reply_text(
                "Maximum 8 UIDs allowed per command",
                parse_mode='Markdown'
            )
            await delete_message_later(context, update.effective_chat.id, error_msg.message_id, 10)
            return
        
        # Get emote ID
        emote_data = EMOTES_DATA[dance_number - 1]
        emote_id = emote_data['id']
        emote_name = emote_data.get('name', f'Dance {dance_number}')
        
        # Send command to API
        import api
        command = {
            'type': 'dance_all',
            'uids': uids,
            'emote_id': emote_id,
            'team_code': team_code,
            'timestamp': asyncio.get_event_loop().time()
        }
        
        api.pending_commands.append(command)
        
        # Create success message
        success_text = f"""
**COMMAND EXECUTED** ✅

**Emote:** {emote_name}
**Dance Number:** {dance_number}
**Team Code:** {team_code}
**Players:** {len(uids)}
**UIDs:** {' '.join(uids[:3])}{'...' if len(uids) > 3 else ''}

Processing now...
        """
        
        sent_msg = await update.message.reply_text(success_text, parse_mode='Markdown')
        await delete_message_later(context, update.effective_chat.id, sent_msg.message_id, 10)
        
    except ValueError:
        error_msg = await update.message.reply_text(
            "Invalid dance number. Must be an integer.",
            parse_mode='Markdown'
        )
        await delete_message_later(context, update.effective_chat.id, error_msg.message_id, 10)
    except Exception as e:
        error_msg = await update.message.reply_text(
            f"Error: {str(e)[:100]}",
            parse_mode='Markdown'
        )
        await delete_message_later(context, update.effective_chat.id, error_msg.message_id, 10)

async def unauthorized_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete any unauthorized messages in the group"""
    if is_allowed_group(update) and update.message:
        try:
            await update.message.delete()
        except BadRequest:
            pass

def main():
    """Start the bot with only allowed commands"""
    if not TELEGRAM_BOT_TOKEN:
        print("Bot token not configured")
        return
    
    print("Starting Professional Dance Bot...")
    print(f"Restricted to group: {ALLOWED_GROUP}")
    print(f"Developer: {DEVELOPER}")
    
    # Create application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("dance", dance))
    
    # Delete all other messages in the group
    application.add_handler(
        filters.TEXT & ~filters.COMMAND & filters.Chat(username=ALLOWED_GROUP[1:]),
        unauthorized_message
    )
    
    # Start bot
    print("Bot is running. Only /start and /dance commands available.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()