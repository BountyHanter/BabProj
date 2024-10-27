from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from database.models.user_profile import UserProfile


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    print(f"Сигнал вызван для пользователя {instance.username}, created={created}")
    if created:
        try:
            profile = UserProfile.objects.create(user=instance)
            print(f"UserProfile создан для пользователя {instance.username}")
        except Exception as e:
            print(f"Ошибка при создании UserProfile: {e}")
    else:
        try:
            profile, created = UserProfile.objects.get_or_create(user=instance)
            print(f"UserProfile get_or_create для пользователя {instance.username}, created={created}")
        except Exception as e:
            print(f"Ошибка при получении или создании UserProfile: {e}")
