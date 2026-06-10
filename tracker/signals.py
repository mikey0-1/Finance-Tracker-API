from django.db.models.signals import post_save
from django.dispatch import receiver
from tracker.models import Category

DEFAULT_CATEGORIES = [
    {'name': 'Salary', 'type': 'income'},
    {'name': 'Freelance', 'type': 'income'},
    {'name': 'Food', 'type': 'expense'},
    {'name': 'Transport', 'type': 'expense'},
    {'name': 'Rent', 'type': 'expense'},
    {'name': 'Entertainment', 'type': 'expense'},
    {'name': 'Healthcare', 'type': 'expense'},
    {'name': 'Utilities', 'type': 'expense'},
]

def create_default_categories(sender, instance, created, **kwargs):
    if created:
        Category.objects.bulk_create([
            Category(user=instance, name=c['name'], type=c['type'])
            for c in DEFAULT_CATEGORIES
        ])
