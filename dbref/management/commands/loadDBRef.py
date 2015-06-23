# -*- coding: UTF-8 -*-
from django.core.management.base import BaseCommand, CommandError
from django.core import serializers
from django.utils.encoding import *
from dbref.models import Product, Brand, Association, Category, Company, Site
from django.core.exceptions import ObjectDoesNotExist, FieldError
import csv
import re
from decimal import *

class Command(BaseCommand):

    def cleanString(self, string):
        substr_list = string.split()
        return ' '.join(substr_list)

    def parseURL(self, url_string):
        match = re.search("(?P<url>https?://[^\s]+)", url_string)
        if match is None:
            match = re.search("(?P<url>www.[^\s]+)", url_string)
        if match is None:
            match = re.search("(?P<url>[^\s]+.com)", url_string)
        if match is None:
            return None
        return match.group("url")

    def parseValidationDate(self, date_string):
        match = re.search(r'(?P<date>Val[i]*d\xc3\xa9\s*le\s*\d+\w*\s+[\wàâäôéèëêïîçùûüÿæœÀÂÄÔÉÈËÊÏÎŸÇÙÛÜÆŒ]+\s+\d*)', 
                            date_string, re.UNICODE)
        if match is None:
            return None
        return match.group("date")

    def parseBrand(self, info):
        return_value = {}

        " Extract Brand Names "
        brand = info.pop(0)
        brand_list = brand.split('/')
        brand_list = map(lambda y: y.strip(), brand_list)
        return_value['name'] = brand_list

        " Extract URL "
        url_list=[]
        rem_list=[]
        for element in info:
            url = self.parseURL(element.strip())
            if url is not None:
                url_list.append(url)
                rem_list.append(element)
        for element in rem_list:
            info.remove(element)
        return_value['url'] = url_list

        " Extract Validation Date "
        for element in info:
            date = self.parseValidationDate(element.strip())
            if date is not None:
                info.remove(element)
                break;
        return_value['validation_date'] = date

        " Note "
        return_value['note'] = self.cleanString('. '.join(info))

        return return_value

    def parseProduct(self, info):
        #if info[1] != '1' and info[1] != '':
        #    print "Warning: expected quantity = 1 or null:"
        #    print info
        if info[0] == 'Non disponible' or info[0] == 'Non Disponible':
            return None
            
        if info[2] == '':
            format = Decimal(0)
        else:
            format = Decimal(info[2])
            
        if info[3] == '':
            price = Decimal(0)
        else:
            price = Decimal(info[3])
            
        if info[0] == '':
            print "Warning: unknown equivalent product. %s" % info
            
        return { 'name': self.cleanString(info[0]), 'format': format, 'price': price }
        
    def parseBothProducts(self, info):
        " Extract equivalent product "
        refProduct = self.parseProduct(info)

        " Extract gluten-free product "
        del info[0:5]
        gluten_free = self.parseProduct(info)
        if gluten_free is None:
            print "ERROR: Gluten Free product is NULL!"

        return [ refProduct, gluten_free ]
    
    def return_or_create_Company(self, brand_info):
        name = brand_info['name'].pop(0)
        if (Brand.objects.filter(name=name).exists()):
            new_company = None
            brand = Brand.objects.get(name=name)
            brand.company.validation_date == smart_text(brand_info['validation_date'])
            if (brand.company.validation_date != smart_text(brand_info['validation_date'])) or \
               (brand.company.note != smart_text(brand_info['note'])):
               raise RuntimeError("Existing brand is not from the expected company")
        else:
            new_company = Company(  validation_date = brand_info['validation_date'],
                                    note = brand_info['note'] )
            new_company.save()
            brand = Brand(name=name, company=new_company)
            brand.save()

        for branding in brand_info['name']:
            if new_company is None:
                if Brand.objects.filter(name=branding).exists():
                    if brand.company is not Brand.objects.get(name=branding).company:
                        raise RuntimeError("Multi-brand not pointing to the same company")
                else:
                    raise RuntimeError("All brand names must all exists or all not exists")
            else:
                if Brand.objects.filter(name=branding).exists():
                    raise RuntimeError("All brand names must all exists or all not exists")
                else:
                    new_brand = Brand(name=branding, company=new_company)
                    new_brand.save()

        for url in brand_info['url']:
            if not brand.company.site_set.filter(domain=url).exists():
                new_site = Site(domain=url, company=brand.company)
                new_site.save()

        return brand.company
                                
    def handle(self, *args, **options):
        with open("SG BD de Reference 3786.txt", "r") as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            context = -1
            line = 0
            for row in reader:
                line += 1
                if len(row) != 0:
                
                    if row[0] == 'Produits avec gluten \xc3\xa9quivalent' or \
                       row[0] == 'Equivalent non-gluten-free products':
                        info = row[5].split("\n")
                        brand_info = self.parseBrand(info)
                        context = 0
                        category = None
                        try:
                            company = self.return_or_create_Company(brand_info)
                        except RuntimeError as e:
                            print e
                            break
                        continue
                        
                    if context == -1:
                        continue
                        
                    if row[0] == 'Description':
                        if context != 0:
                            print "Unexpected Description in row[0]"
                            print "Line %s" % line
                            print row
                            continue
                        context = 1
                        continue
                        
                    if row[0] == '' and row[1] == '' and row[2] == '' and row[3] == '' and row[4] == '' and row[5] == '':
                        if context == 0:
                            print "Unexpected '' in row[0]"
                            print "Line %s, context %s" % (line, context)
                            print row
                            continue
                        if category is not None:
                            category = None
                        context = 2
                        continue
                        
                    if row[0] == '' and row[1] == '' and row[2] == '' and row[3] == '' and row[4] == '' and row[5] != '':
                        if context == 0 or context == 1:
                            print "Unexpected '' in row[0]"
                            print "Line %s, context %s" % (line, context)
                            print row
                            continue
                        # Note: context 3 can be repeated
                        note = self.cleanString(row[5])
                        if not Category.objects.filter(note=note).exists():
                            category = Category ( note = note )
                            category.save()
                            if len(category.note) > 800:
                                print "Category note exceed 800, -> %s" % len(category.note)
                        context = 3
                        continue
                        
                    if context == 1:
                        print "Unexpected data"
                        print "Line %s, context %s" % (line, context)
                        print row
                        continue
                    
                    # Note: row[0] may be equal to 'Non disponible'
                    products = self.parseBothProducts(row)
                    
                    if products[0] is None:
                        refProduct = None
                    else:
                        if not Product.objects.filter (
                                description = products[0]['name'],
                                unit = products[0]['format'],
                                price = products[0]['price'],
                                gluten_free = False,
                                company = None,
                                category = None
                            ).exists():
                            refProduct = Product (
                                description = products[0]['name'],
                                unit = products[0]['format'],
                                price = products[0]['price'],
                                gluten_free = False,
                                company = None,
                                category = None
                            )
                            if len(refProduct.description) > 200:
                                print "refProduct description exceed 800, -> %s" % len(refProduct.description)
                            refProduct.save()
                        
                    if products[1] is None:
                        gluten_free = None
                        print "Gluten-Free product is Null"
                    else:
                        if Product.objects.filter (
                                description = products[1]['name'],
                                unit = products[1]['format'],
                                price = products[1]['price'],
                                gluten_free = True,
                                company = company,
                                category = category
                            ).exists():
                            print "Warning: Duplicate gluten-free product."
                        else:
                            gluten_free = Product (
                                description = products[1]['name'],
                                unit = products[1]['format'],
                                price = products[1]['price'],
                                gluten_free = True,
                                company = company,
                                category = category
                            )
                            gluten_free.save()
                    
                    try:
                        association = Association.objects.get (
                            equivalent = refProduct,
                            gluten_free = gluten_free
                        )
                        print "Warning: Duplicate association"
                    except ObjectDoesNotExist as e:
                        association = Association (
                            equivalent = refProduct,
                            gluten_free = gluten_free
                        )
                        association.save()
                    context = 4

 
