from django.core.management.base import BaseCommand

from tg_bot import Bot



class Command(BaseCommand):
    help = 'Runs the bot'

    def handle(self, *args, **options):
        bot = Bot()