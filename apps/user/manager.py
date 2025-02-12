from django.contrib.auth.models import BaseUserManager



class CustomUserManager(BaseUserManager):
    """custom user manager class"""
    use_in_migration = True

    def _create_user(self, username, email, password, **extra_fields):
        """
        Creates and saves a User with the given phone and password.
        """
        if not username:
            raise ValueError('The username is required.')
        if not email:
            raise ValueError('The email is required.')
        
        username =  str(username).strip()
        email = self.normalize_email(email)

        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_active', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        username =  str(username).strip()
        return self._create_user(username, email, password, **extra_fields)
