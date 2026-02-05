from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager
)
from django.db.models.signals import post_save
from django.dispatch import receiver

# -----------------------------
# USER MANAGER
# -----------------------------
class UserAccountManager(BaseUserManager):
    def create_user(self, email, name, role='user', password=None):
        if not email:
            raise ValueError('Users must have an email address')
        
        if not password:
            raise ValueError('Users must have a password')

        email = self.normalize_email(email).lower()

        user = self.model(
            email=email,
            name=name,
            role=role
        )

        user.set_password(password)
        user.is_active = True
        user.save(using=self._db)
        return user

    def create_realtor(self, email, name, password=None):
        return self.create_user(
            email=email,
            name=name,
            role='realtor',
            password=password
        )

    def create_superuser(self, email, name, password=None):
        if not password:
            raise ValueError('Superusers must have a password.')
        user = self.create_user(
            email=email,
            name=name,
            role='admin',
            password=password
        )
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save(using=self._db)
        return user


# -----------------------------
# USER MODEL
# -----------------------------
class UserAccount(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('realtor', 'Realtor'),
        ('user', 'User'),
    )

    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=230)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

    objects = UserAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email
    
class RealtorProfile(models.Model):
    user = models.OneToOneField(
        UserAccount,
        on_delete=models.CASCADE,
        related_name='realtor_profile'
    )
    phone = models.CharField(max_length=20)
    company_name = models.CharField(max_length=150)
    license_number = models.CharField(max_length=150, unique=True)
    bio = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now= True)

    def __str__(self):
        return f"{self.user.name} - Realtor"
    

# -----------------------------
# SIGNALS
# -----------------------------
@receiver(post_save, sender=UserAccount)
def create_realtor_profile(sender, instance, created, **kwargs):
    """
    Automatically create a RealtorProfile when a realtor user is created
    """
    if created and instance.role == 'realtor':
        RealtorProfile.objects.create(user=instance)




