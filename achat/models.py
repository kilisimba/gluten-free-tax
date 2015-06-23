import math
from decimal import *
from django.db import models
from dbref.models import Association

class Achat(models.Model):
    date = models.DateField()
    description = models.CharField(max_length=200, blank=True)
    brand = models.CharField(max_length=200, blank=True)
    unit = models.DecimalField(default=0, max_digits=8, decimal_places=2)
    price = models.DecimalField(default=0, max_digits=8, decimal_places=2)
    equivalent = models.CharField(max_length=200, blank=True)
    equivalent_unit = models.DecimalField(verbose_name='unit', default=0, max_digits=8, decimal_places=2)
    equivalent_price = models.DecimalField(verbose_name='price', default=0, max_digits=8, decimal_places=2)
    quantity = models.SmallIntegerField(verbose_name='qty', default=1)
    taxable = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date', '-pk']	# Odered by transaction's date

class Pending(models.Model):
    achat = models.OneToOneField(Achat, default=0, primary_key=True)
