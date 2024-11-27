import os
import sqlite3
import datetime
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Load environment variables from .env file
load_dotenv()
API_KEY = os.getenv('TELEGRAM_API_KEY')

# Setup SQLite database
def setup_database():
    conn = sqlite3.connect('food_records.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS food_records (
            date TEXT,
            username TEXT,
            food TEXT,
            PRIMARY KEY (date, username)
        )
    ''')
    conn.commit()
    conn.close()

# Command handler for /food
async def food(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if datetime.datetime.now().weekday() == 2:  # 2 is Wednesday
        if len(context.args) < 1:
            await update.message.reply_text("Please provide the name of the food.")
            return

        food_name = ' '.join(context.args)
        date = datetime.datetime.now().strftime('%Y-%m-%d')
        username = update.message.from_user.username

        # Save to database
        conn = sqlite3.connect('food_records.db')
        c = conn.cursor()
        try:
            # Use INSERT OR REPLACE to handle upsert logic
            c.execute("INSERT OR REPLACE INTO food_records (date, username, food) VALUES (?, ?, ?)", (date, username, food_name))
            conn.commit()
            await update.message.reply_text("ok")
        except Exception as e:
            await update.message.reply_text("ko")
        finally:
            conn.close()
    else:
        await update.message.reply_text("This command can only be used on Wednesdays.")

# Command handler for /summary
async def summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today = datetime.datetime.now().strftime('%Y-%m-%d')  # Get today's date in 'YYYY-MM-DD' format
    conn = sqlite3.connect('food_records.db')
    c = conn.cursor()

    # Modify the query to include the condition for today's date
    c.execute("SELECT username, food FROM food_records WHERE date = ?", (today,))
    records = c.fetchall()
    conn.close()

    if records:
        summary_text = "\n".join([f"{username}: {food}" for username, food in records])
        await update.message.reply_text(summary_text)
    else:
        await update.message.reply_text("No records found for today.")


def main():
    # Use the API key from the environment variable
    application = Application.builder().token(API_KEY).build()

    # Setup database
    setup_database()

    # Register command handlers
    application.add_handler(CommandHandler('food', food))
    application.add_handler(CommandHandler('summary', summary))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()