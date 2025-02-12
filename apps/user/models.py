import uuid
from django.db import models
from django.utils import timezone
from django.utils.html import mark_safe
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from apps.user.manager import CustomUserManager
from django.utils.translation import gettext_lazy as _


def user_img_upload_location(instance, filename):
    file_extension = filename.split('.')[-1]
    return f"users/{instance.username}-{uuid.uuid4()}.{file_extension}"


# Create your models here.
class User(AbstractUser):
    email           = models.EmailField(_('Email'), null=False, blank=False, max_length=120, unique=True)
    username        = models.CharField(_('Username'), null=False, blank=False, max_length=20, unique=True)
    first_name      = models.CharField(_('First Name'), max_length=150, null=True, blank=True)
    last_name       = models.CharField(_('Last Name'), max_length=150, null=True, blank=True)
    is_active       = models.BooleanField(_('Active'), default=False, help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.")
    is_admin        = models.BooleanField(_('Employee'),default=False, help_text="Designates whether the user should be treated as an employee/admin.")
    is_staff        = models.BooleanField(_('Backend Access'), default=False, help_text="Designates whether the user can log into this admin site.")
    is_superuser    = models.BooleanField(_('Superuser'), default=False, help_text="Designates that this user has all permissions without explicitly assigning the models.")
    email_verified  = models.BooleanField(_('Email Verified'), default=False)
    photo           = models.ImageField(_('Profile'), upload_to=user_img_upload_location, default=None, blank=True, null=True)
    contact_number  = PhoneNumberField(_('Phone Number'), blank=True, null=True, max_length=15)
    bio             = models.TextField(_("Bio"), null=True, blank=True)
    last_login      = models.DateTimeField(_('Last Login'), auto_now=True)
    date_joined     = models.DateTimeField(_('Date Joined'), auto_now_add=True)

    objects         = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'username',
        'first_name',
        'last_name',
    ]

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
    

    def profile_photo(self):
        if self.photo:
            return mark_safe(f'<img src="{self.photo.url}" width="50" height="50" style="border-radius: 25px; box-shadow: 1px 1px 5px #808080;"/>')
        
        # Get initials or use a default
        initials = getattr(self, 'username', 'U')[0].upper() if hasattr(self, 'username') else 'U'
    
        return mark_safe(f'''
            <div style="
                width: 50px;
                height: 50px;
                background: linear-gradient(45deg, #3498db, #2980b9);
                border-radius: 25px;
                box-shadow: 1px 1px 5px #808080;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-weight: bold;
                font-size: 20px;
                font-family: Arial, sans-serif;
            ">
                {initials}
            </div>
        ''')

    def full_name(self):
        if not self.first_name and not self.last_name:
            return f"{self.username}".title()
        return f"{self.first_name} {self.last_name}".title()

    def __str__(self):
        return self.full_name()
