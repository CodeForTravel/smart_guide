from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    class UserType(models.TextChoices):
        SYS_ADMIN = "sys_admin", "System Admin"
        USER = "user", "End User"

    user_type = models.CharField(
        max_length=20,
        choices=UserType.choices,
        default=UserType.USER,
    )
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"  # this makes email the login field
    REQUIRED_FIELDS = []  # fields required when creating superuser

    @property
    def is_sysadmin(self):
        if self.user_type == self.UserType.SYS_ADMIN:
            return True
        return False

    @property
    def is_user(self):
        if self.user_type == self.UserType.USER:
            return True
        return False


class UserPreferences(models.Model):
    class LanguageChoices(models.TextChoices):
        EN = "en", "English"
        AR = "ar", "Arabic"
        DK = "dk", "Danish"
        DE = "de", "German"
        ES = "es", "Spanish"
        FR = "fr", "French"
        IT = "it", "Italian"
        NL = "nl", "Dutch"
        PT = "pt", "Portuguese"
        RU = "ru", "Russian"
        ZH = "zh", "Chinese"

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    language = models.CharField(max_length=2, default=LanguageChoices.EN, choices=LanguageChoices.choices)
    notification = models.BooleanField(default=True)
    interest_history_score = models.IntegerField(default=5, validators=[MinValueValidator(0), MaxValueValidator(10)])
    interest_food_score = models.IntegerField(default=5, validators=[MinValueValidator(0), MaxValueValidator(10)])
    interest_architecture_score = models.IntegerField(
        default=5, validators=[MinValueValidator(0), MaxValueValidator(10)]
    )
    interest_nature_score = models.IntegerField(default=5, validators=[MinValueValidator(0), MaxValueValidator(10)])
    narration_length_default = models.IntegerField(default=400)
    walking_speed_estimate = models.IntegerField(default=4)  # in km/h

    def __str__(self):
        return f"{self.user.email} Preferences"


@receiver(post_save, sender=CustomUser)
def create_user_preferences(sender, instance, created, **kwargs):
    if created:
        UserPreferences.objects.create(user=instance)
