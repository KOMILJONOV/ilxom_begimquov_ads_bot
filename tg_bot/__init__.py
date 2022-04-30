import time
from setuptools import Command
from telegram import *
from telegram.ext import *

from tg_bot.constants import TOKEN
from bot.models import Admin, User


def get_user(update:Update):
    user = update.message.from_user if update.message else update.callback_query.from_user
    return user, User.objects.filter(chat_id=user.id).first()

db: User = None
MEDIA, TEXT, CHECK = range(3)
class Bot(Updater):
    def __init__(self):
        super().__init__(token=TOKEN)

        self.dispatcher.add_handler(CommandHandler('start', self.start))
        self.dispatcher.add_handler(ConversationHandler(
            [
                CommandHandler('post', self.post),
            ],
            {
                MEDIA: [
                    MessageHandler(Filters.photo, self.media_photo),
                    MessageHandler(Filters.video, self.media_video),
                    CommandHandler('skip', self.skip_media),
                ],
                TEXT: [
                    MessageHandler(Filters.text, self.text),
                ],

            },
            []
        ))

        self.idle()
    
    def start(self, update:Update, context:CallbackContext):
        user, db = get_user(update)
        update.message.reply_text("Hello!")
        if not db:
            User.objects.create(chat_id=user.id)
    
    def post(self, update:Update,context:CallbackContext):
        user, db = get_user(update)
        admin = Admin.objects.filter(chat_id=user.id).first()
        if admin:
            context.user_data['post'] = {}
            user.send_message("Iltimos post uchun surat yoki video yuboring!")
            return MEDIA
        
    def media_photo(self, update:Update, context:CallbackContext):
        user, db = get_user(update)
        context.user_data['post']['photo'] = update.message.photo[-1].file_id
        user.send_message("Iltimos post uchun maqolani yuboring!", parse_mode=ParseMode.HTML)
        return TEXT
    
    def media_video(self, update:Update, context:CallbackContext):
        user, db = get_user(update)
        context.user_data['post']['video'] = update.message.video.file_id
        user.send_message("Iltimos post uchun maqolani yuboring!", parse_mode=ParseMode.HTML)
        return TEXT
    
    def skip_media(self, update:Update, context:CallbackContext):
        user, db = get_user(update)
        user.send_message("Iltimos post uchun maqolani yuboring!", parse_mode=ParseMode.HTML)
        return TEXT
    
    def text(self, update:Update, context:CallbackContext):
        user, db = get_user(update)
        context.user_data['post']['text'] = update.message.text
        user.send_message("Postingiz tayyor")

        if context.user_data.get('photo'):
            user.send_photo(context.user_data['photo'], caption=context.user_data['text'], parse_mode=ParseMode.HTML, caption_entities=update.message.entities)
        elif context.user_data.get('video'):
            user.send_video(context.user_data['video'], caption=context.user_data['text'], parse_mode=ParseMode.HTML, caption_entities=update.message.entities)
        else:
            user.send_message(context.user_data['text'], parse_mode=ParseMode.HTML, caption_entities=update.message.entities)

        return CHECK
    
    def check(self, update:Update, context:CallbackContext):
        user, db = get_user(update)
        if update.message.text.startswith("✅"):
            peer = 0
            for db_user in User.objects.all():
                if context.user_data.get('photo'):
                    self.bot.send_message(db_user.chat_id,context.user_data['photo'], caption=context.user_data['text'], parse_mode=ParseMode.HTML, caption_entities=update.message.entities)
                elif context.user_data.get('video'):
                    self.bot.send_photo(db_user.chat_id,context.user_data['video'], caption=context.user_data['text'], parse_mode=ParseMode.HTML, caption_entities=update.message.entities)
                else:
                    self.bot.send_video(db_user.chat_id,context.user_data['text'], parse_mode=ParseMode.HTML, caption_entities=update.message.entities)
                peer += 1
                if peer == 20:
                    time.sleep(1)
                    peer = 0

            user.send_message("Postingiz muvaffaqiyatli yuborildi!")
        elif update.message.text.startswith("❌"):
            user.send_message("Postingiz o'chirildi")