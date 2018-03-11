from django.db import models

# Create your models here.
from django.contrib.auth.models import User


class Publisher(models.Model):
    name = models.CharField(max_length=255)
    natural_id = models.CharField(max_length=255)


class UserProfile(models.Model):
    USER_TYPE_AUTHOR = 'AU'
    USER_TYPE_MEDIA_EXECUTIVE = 'ME'
    USER_TYPE_EDITOR = 'ET'
    USER_TYPES = (
        (USER_TYPE_AUTHOR,'Author'),
        (USER_TYPE_MEDIA_EXECUTIVE,'Media Executive'),
        (USER_TYPE_EDITOR,'Editor'),
    )

    user_type = models.CharField(choices=USER_TYPES,default=USER_TYPE_AUTHOR)
    publisher = models.ForeignKey(Publisher)
    user = models.OneToOneField(User)


class BookStore(models.Model):
    publisher = models.ManyToManyField(Publisher)

    #: 2 fields unique together, 'natural keys'
    name = models.CharField(max_length=255)
    city = models.CharField(max_length=255)


class NumericalMetaData(models.Model):
    #: TODO: Generic ForeignKey to BookStore AND Publisher to allow for that dependency relationship to be tested
    bookstore = models.ForeignKey(BookStore)

    entry_date = models.DateField()
    entry_datetime = models.DateTimeField()

    number_type1 = models.IntegerField()
    number_type2 = models.BigIntegerField()
    number_type3 = models.FloatField()
    number_type4 = models.DecimalField()