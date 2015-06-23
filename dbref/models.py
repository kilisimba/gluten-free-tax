from django.db import models


class Note(models.Model):
    note = models.TextField(max_length=800)
    
    def __unicode__(self): # Python 3: def __str__(self):
        return self.note

class Company(models.Model):
    name =  models.CharField(max_length=200, default='Unknown')
    validation_date = models.CharField(max_length=100, blank=True, null=True)
    certification = models.CharField(max_length=200, blank=True, null=True)
    note = models.ForeignKey(Note, blank=True, null=True)
    
    def brands(self):
        return ' / '.join(self.brand_set.values_list('name', flat=True))
        
    def __unicode__(self):
        return self.brands()
 
class Brand(models.Model):
    name = models.CharField(max_length=200)
    company = models.ForeignKey(Company, blank=True, null=True)
    
    def __unicode__(self): # Python 3: def __str__(self):
        return self.name

    class Meta:
        ordering = ['name'] 

class Site(models.Model):
    domain = models.CharField(max_length=200)
    company = models.ForeignKey(Company)

class Category(models.Model):
    note = models.TextField(max_length=800)
    
    def __unicode__(self): # Python 3: def __str__(self):
        return self.note
 
    class Meta:
        verbose_name_plural = "Categories"

class Product(models.Model):
    description = models.CharField(max_length=200)
    unit = models.DecimalField(default=0, max_digits=8, decimal_places=2)
    price = models.DecimalField(default=0, max_digits=8, decimal_places=2)
    gluten_free = models.BooleanField(default=False)
    company = models.ForeignKey(Company, blank=True, null=True)
    category = models.ForeignKey(Category, blank=True, null=True)
    note = models.ForeignKey(Note, blank=True, null=True)
    
    def __unicode__(self): # Python 3: def __str__(self):
        return self.description
 
class Association(models.Model):
    equivalent = models.ForeignKey(Product, blank=True, null=True, \
                                    related_name='nonGF', verbose_name='non-gluten free')
    gluten_free = models.ForeignKey(Product, related_name='GF')

    class Meta:
        verbose_name = "Lookup Table"
        ordering = ['gluten_free__description', 'equivalent__description']
