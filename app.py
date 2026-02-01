import os
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import telebot

# --- Configuration ---
TOKEN = '8495906224:AAHj4lX8WTXIhrwsMSGVvZInsIP4HZiMotE' # BotFather ဆီက Token ဒီမှာထည့်ပါ
SECRET_KEY = "mysecretkey"
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)
# Database Setup (SQLite)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///media.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- Database Model ---
class Media(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(20), nullable=False) # Movie or Music
    poster_url = db.Column(db.String(500), nullable=False)
    content_url = db.Column(db.String(500), nullable=False) # Video/Audio Link
    review = db.Column(db.Text, nullable=True)

# App စ run ရင် Database ဆောက်မယ်
with app.app_context():
    db.create_all()

# --- Routes (Mini App) ---

# Home Page (User View)
@app.route('/')
def index():
    movies = Media.query.filter_by(category='Movie').all()
    music = Media.query.filter_by(category='Music').all()
    return render_template('index.html', movies=movies, music=music)

# Admin API: Add New Media
@app.route('/add', methods=['POST'])
def add_media():
    data = request.json
    new_media = Media(
        title=data['title'],
        category=data['category'],
        poster_url=data['poster_url'],
        content_url=data['content_url'],
        review=data['review']
    )
    db.session.add(new_media)
    db.session.commit()
    return jsonify({"message": "Success"})

# Admin API: Delete Media
@app.route('/delete/<int:id>', methods=['DELETE'])
def delete_media(id):
    media = Media.query.get_or_404(id)
    db.session.delete(media)
    db.session.commit()
    return jsonify({"message": "Deleted"})

# --- Telegram Bot Command ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    # Mini App ဖွင့်ဖို့ Button
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    # မှတ်ချက် - URL နေရာမှာ Deploy လုပ်ပြီးရလာတဲ့ Web URL ကိုထည့်ရမယ်
    web_app = telebot.types.WebAppInfo("https://your-app-url.onrender.com") 
    markup.add(telebot.types.KeyboardButton(text="Open Mini App 🎬", web_app=web_app))
    bot.send_message(message.chat.id, "မင်္ဂလာပါ! ရုပ်ရှင်နှင့် သီချင်းများကြည့်ရန် အောက်ပါခလုတ်ကို နှိပ်ပါ။", reply_markup=markup)

# --- Run Server ---
if __name__ == '__main__':
    # Bot ကိုသီးသန့် Thread တစ်ခုနဲ့ run ဖို့လိုနိုင်ပါတယ် (Local run ဖို့အတွက်သာ)
    # Deploy လုပ်ရင် Webhook သုံးတာ ပိုကောင်းပါတယ်
    app.run(debug=True, host='0.0.0.0', port=5000)
  
