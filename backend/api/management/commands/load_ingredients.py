import os
import csv

import django
from django.conf import settings
from django.core.management import BaseCommand
from django.db.utils import IntegrityError

from recipes.models import Ingredient

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.foodgram.settings')

django.setup()


class Command(BaseCommand):
    help = "Load data from csv file"

    def handle(self, *args, **kwargs):
        try:
            with open(
                    f"{settings.BASE_DIR.parent}/data/ingredients.csv", "r",
                    encoding="utf-8"
            ) as csv_file:
                reader = csv.reader(csv_file)
                objects = (
                    Ingredient(name=data[0], measurement_unit=data[1])
                    for data in reader
                )
                Ingredient.objects.bulk_create(objects)
        except IntegrityError:
            pass
        except FileNotFoundError:
            raise Exception(
                "Ошибка при импорте файла базы данных. "
                "Проверьте наличие файла ingredients.csv "
                f"по адресу: {settings.BASE_DIR}/data/"
            )
        self.stdout.write(self.style.SUCCESS("Successfully load data"))
