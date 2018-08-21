from django.db import models

# Create your models here.
from django.contrib.auth.models import User


class Company(models.Model):
    name = models.CharField(max_length=255,null=True)
    natural_id = models.CharField(max_length=255)


class UserProfile(models.Model):
    USER_TYPE_BOSS = 'BS'
    USER_TYPE_WORKER = 'WK'
    USER_TYPES = (
        (USER_TYPE_BOSS,'Boss'),
        (USER_TYPE_WORKER,'Worker'),
    )

    user_type = models.CharField(max_length=2,choices=USER_TYPES,default=USER_TYPE_WORKER)
    company = models.ForeignKey(Company,on_delete=models.CASCADE)
    user = models.OneToOneField(User,on_delete=models.CASCADE)


class Tag(models.Model):
    company = models.ForeignKey(Company,on_delete=models.CASCADE)
    created_by = models.ForeignKey(UserProfile,on_delete=models.CASCADE)

    name = models.CharField(max_length=255,default='')
    slug = models.CharField(max_length=255,default='')
    rank = models.IntegerField(null=False)


class Image(models.Model):
    #: Maybe not (??)
    company = models.ForeignKey(Company,on_delete=models.CASCADE)

    # tag = models.ManyToManyField(Tag)
    tag = models.ManyToManyField(Tag)  #,on_delete=models.CASCADE) #: Pretend for now

    name = models.CharField(max_length=255,null=False)
    path = models.CharField(max_length=255,null=False)


class Document(models.Model):
    slug = models.CharField(max_length=255,null=False)
    image = models.ForeignKey(Image, on_delete=models.CASCADE)