import logging
from pymongo import MongoClient
from telegram import Update, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, InlineQueryHandler, CallbackContext, MessageHandler, Filters

# Setup logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# MongoDB setup
MONGO_URI = "YOUR_MONGO_DB_CONNECTION_STRING"  # Replace with your MongoDB URI
client = MongoClient(MONGO_URI)
db = client['game_db']
games_collection = db['games']

def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"Hello {user.first_name}, use /play to start a game!")

def inline_query(update: Update, context: CallbackContext) -> None:
    query = update.inline_query.query
    if query == "start":
        results = [
            InlineQueryResultArticle(
                id='1',
                title="Start Game",
                input_message_content=InputTextMessageContent("Game Started!")
            )
        ]
        update.inline_query.answer(results)

def play(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    chat_id = update.effective_chat.id
    game_id = f"{chat_id}_{user.id}"
    
    # Store game data in MongoDB
    games_collection.insert_one({
        'game_id': game_id,
        'user1_id': user.id,
        'user2_id': None,
        'moves': []
    })
    
    context.bot.send_message(chat_id=update.effective_chat.id, text="Game started! You can now play with your friends.")

def handle_move(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    chat_id = update.effective_chat.id
    user = update.effective_user

    game = games_collection.find_one({'game_id': f"{chat_id}_{user.id}"})

    if game:
        moves = game['moves']
        moves.append(text)  # Append the move to existing moves
        games_collection.update_one({'game_id': f"{chat_id}_{user.id}"}, {'$set': {'moves': moves}})
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"Move recorded: {text}")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="No active game found.")

def main() -> None:
    # Replace 'YOUR_TOKEN' with your bot's API token
    updater = Updater("7273900330:AAFCXXJUHshcxLUgpV8SmXf2VgHA_zIr0FM")

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Register command and handler functions
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("play", play))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_move))
    dp.add_handler(InlineQueryHandler(inline_query))

    # Start the Bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
