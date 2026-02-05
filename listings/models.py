from django.conf import settings
from django.db import models, IntegrityError, transaction
from django.utils.text import slugify


class Listing(models.Model):
    class CategoryChoices(models.TextChoices):
        FOR_SALE = 'FOR_SALE', 'For Sale'
        FOR_RENT = 'FOR_RENT', 'For Rent'
        FOR_BUY = 'FOR_BUY', 'For Buy'

    realtor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    realtor_email = models.EmailField(max_length=255, blank=True )
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    location = models.CharField(max_length=255)
    bedrooms = models.IntegerField(default=0)
    bathrooms = models.DecimalField(max_digits=2,decimal_places=1, default=0.0)
    category = models.CharField(max_length=20, choices=CategoryChoices.choices, default=CategoryChoices.FOR_SALE)
    created_at = models.DateTimeField(auto_now_add=True)
    main_photo = models.ImageField(upload_to='listings/',)
    photo_1 = models.ImageField(upload_to='listings/', blank=True, null=True)
    photo_2 = models.ImageField(upload_to='listings/', blank=True, null=True)  
    photo_3 = models.ImageField(upload_to='listings/', blank=True, null=True)
    is_published = models.BooleanField(default=False)


    def delete(self, using=None, keep_parents=False):
        if self.main_photo:
          self.main_photo.storage.delete(self.main_photo.name)

        if self.photo_1:
          self.photo_1.storage.delete(self.photo_1.name)

        if self.photo_2:
          self.photo_2.storage.delete(self.photo_2.name)

        if self.photo_3:
          self.photo_3.storage.delete(self.photo_3.name)

        super().delete(using=using, keep_parents=keep_parents)


    def save(self, *args, **kwargs):
      if not self.slug:
        base_slug = slugify(self.title)
        for i in range(100):
            self.slug = base_slug if i == 0 else f"{base_slug}-{i}"
            try:
                with transaction.atomic():
                    super().save(*args, **kwargs)
                    break  # Exit loop after successful save
            except IntegrityError:
                continue
        else:
            raise IntegrityError("Could not generate a unique slug")
      else:
        super().save(*args, **kwargs)



    def __str__(self):
        return self.title
