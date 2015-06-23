# -*- coding: UTF-8 -*-
from django.core.management.base import BaseCommand, CommandError
from django.core import serializers
from django.utils.encoding import *
from dbref.models import Product, Brand, Association, Category, Company, Site, Note
from django.core.exceptions import ObjectDoesNotExist, FieldError
from decimal import *
import re
import lxml.html
import lxml.etree
import argparse

red = '\x1b[31m'
highlight = '\x1b[43;31m'
yellow = '\x1b[33m'
green = '\x1b[32m'
reset = '\x1b[0m'

class Command(BaseCommand):
    # args = '<html file>'
    help = 'Parse html file exported from gnumeric using html 4.0'


    def parseURL(self, url_string):
        match = re.search("(?P<url>https?://[^\s]+)", url_string)
        if match is None:
            match = re.search("(?P<url>www.[^\s]+)", url_string)
        if match is None:
            match = re.search("(?P<url>[^\s]+.com)", url_string)
        if match is None:
            return None
        #return match.group("url")
        return url_string

    def parseDate(self, date_string):
#        match = re.search(r'(?P<date>Val[i]*d\xc3\xa9\s*le\s*\d+\w*\s+[\wàâäôéèëêïîçùûüÿæœÀÂÄÔÉÈËÊÏÎŸÇÙÛÜÆŒ]+\s+\d*)', 
#                            date_string, re.UNICODE)
        match = re.search(r'(\d\d?)(er)? .* (\d\d\d\d)', date_string, re.UNICODE)
        if match is None:
            match = re.search(r'(\d\d\d\d) .* (\d\d>)(er)?', date_string, re.UNICODE)
#        if match is None:
#            match = re.search(r'^[Vv]alid', date_string, re.UNICODE)
        if match is None:
            return None
        #return match.group("date")
        return date_string

    def parseCertification(self, certification_string):
        # The order is important: place CSA Australia before CSA. 
        names = ('GFCO', 'HACCP', 'GFCP', 'PCSG', 'NFCA', 'QAI', 'CSA Australie', 'CSA', 'GIG', 'NSF', 'NFC Gluten Guard')
        self.certification = []
        if certification_string == '':
            return
        for name in names:
            if name in certification_string:
                self.certification.append(name)
                certification_string = certification_string.replace(name, '')

        certification_string = certification_string.replace('+', '')
        certification_string = certification_string.replace('/', '')
        certification_string = certification_string.strip()
        if certification_string != '':
            raise RuntimeWarning("Possible missing certification: ", certification_string)

    def parseNote(self, info):
        self.note = info.pop(0)
        if ''.join(info) != '':
            raise RuntimeWarning('Note is followed by "%s" that will be ignored' % ' '.join(info))

    def parseProduct(self, info):
        if info[0] == 'Non disponible' or info[0] == 'Non Disponible':
            return None
        description =  info[0]

        warnings = []
        if info[1] != '1' and info[1] != '':
            warnings.append( (0, "Quantity %s is not expected" % info[1]) )
            
        if info[2] == '':
            product_format = Decimal(0)
        else:
            product_format = Decimal(info[2].replace(',', ''))
            
        if info[3] == '':
            price = Decimal(0)
        else:
            price = Decimal(info[3].replace(',', ''))
            
        if info[4] == '':
            unit_price = Decimal(0)
        else:
            unit_price = Decimal(info[4].replace(',', ''))
            
        if description == '' and product_format == 0 and price == 0 and unit_price == 0:
            return None

        if description == '':
            self.product = None
            raise RuntimeError("Missing description")

        if product_format == 0:
            warnings.append( (1, "Missing product format") )
        else: 
            price_format = Decimal(str(round(price/product_format, 3)))
            if abs(price_format - unit_price) > Decimal(0.001):
                if unit_price == 0:
                    warnings.append( (1, "Missing unit price") )
                else:
                    # This mismatch is due to the format that is truncated
                    # Fix format with unit_price
                    fix_product_format = Decimal(str(round(price/unit_price, 1)))
                    if abs(fix_product_format - product_format) < 1:
                        warnings.append( (0, "Mismatch unit price: unit will be fixed to %s" %  fix_product_format) )
                    else:
                        warnings.append( (0, "Mismatch unit price: fix unit to %s is not recommended. Ignoring unit price" % \
                            fix_product_format) )
            
        self.product = { 'name': info[0], 'format': product_format, 'price': price }
        if warnings != []:
            raise RuntimeWarning(warnings)

    def str_brand(self, brand_name, url, date, certification, note):
        return '\t'+green+'brand: '+reset+'%s, ' % brand_name+ \
                green+'url: '+reset+'%s, ' % url+ \
                green+'date: '+reset+'%s, ' % date+ \
                green+'cert: '+reset+'%s, ' % certification+ \
                green+'note: '+reset+'%s, ' % note

    def parseBrand(self, row):
        brand_name = []
        self.url = []
        self.date = None
        self.brand_note = []
        certification=[]
        newline = False
        for child in row.iter():
            #if self.caption.text == 'Bragg':
            #    print "tag: %s, text: %s, tail: %s" % (child.tag, child.text, child.tail)
            if child.tag == 'br':
                newline = True
            for text in [ child.text, child.tail ]:
                if text is None:
                    continue
                text = text.strip()
                if text == '':
                    continue
                if newline is False:
                    if child.tail is not None and child.tail.strip() == text:
                        newline = True
                    else:
                        brand_name.append(text)
                        continue
                new_url = self.parseURL(text)
                if new_url is not None:
                    self.url.append(new_url)
                    continue
                if self.date is None:
                    self.date = self.parseDate(text)
                    if self.date is not None:
                        continue
                if certification == []:
                    try:
                        self.parseCertification(text)
                    except RuntimeWarning as e:
                        if not self.error_warning : self.stdout.write('Brand: %s' % self.caption.text)
                        self.error_warning += 1
                        self.stdout.write('\t'+highlight+e.args[0]+reset+e.args[1])
                    certification = self.certification
                    if certification != []:
                        continue
                if self.brand_note == []:
                    self.brand_note.append(text)

        self.brand_name = ''.join(brand_name)
        if self.url == []:
            if not self.error_warning : self.stdout.write('Brand: %s' % self.caption.text)
            self.error_warning += 1
            self.stdout.write('\t'+yellow+'Missing URL'+reset)
            self.stdout.write(self.str_brand(self.brand_name, ' '.join(self.url), self.date, \
                ' '.join(certification), ' '.join(self.brand_note)))
        if self.date is None:
            if not self.error_warning : self.stdout.write('Brand: %s' % self.caption.text)
            self.error_warning += 1
            self.stdout.write('\t'+yellow+'Missing Date'+reset)
            self.stdout.write(self.str_brand(self.brand_name, ' '.join(self.url), self.date, \
                ' '.join(certification), ' '.join(self.brand_note)))

    def parseProducts(self, row, company, save):
        category_obj = None
        note_obj = None
        note = []
        for product in row.itersiblings():

            if product.find("td").get('colspan') == '5':
                list_note = [ cell.xpath("string()").strip() for cell in product.iterfind(".//td")]
                try:
                    self.parseNote(list_note[1:-2])
                except RuntimeWarning as e:
                    if not self.error_warning : self.stdout.write('Brand: %s' % self.caption.text)
                    self.error_warning += 1
                    self.stdout.write('\t'+yellow+'%s' % e+reset)
                    self.stdout.write('\t%s' % list_note)
                if self.note != '':
                    note.append(self.note)
                continue

            list_product = [ cell.xpath("string()").strip() for cell in product.iterfind(".//td")]
            if ''.join(list_product).strip() == '':
                continue

            # Parse non-GF 
            try:
                self.parseProduct(list_product[:5])
            except RuntimeError as e:
                if not self.error_warning : self.stdout.write('Brand: %s' % self.caption.text)
                self.error_warning += 1
                self.stdout.write('\t'+red+'%s' % e+reset)
                self.stdout.write('\t%s' % list_product[:5])
            except RuntimeWarning as warnings:
                if not self.error_warning : self.stdout.write('Brand: %s' % self.caption.text)
                self.error_warning += 1
                for warning in warnings.args[0]:
                    self.stdout.write('\t'+yellow+'%s' % warning[1]+reset)
                self.stdout.write('\t%s' % list_product[:5])
            if self.product is None:
                continue
            refProduct = Product (
                description = self.product['name'],
                unit = self.product['format'],
                price = self.product['price'],
                gluten_free = False,
                company = None,
                category = None,
                note = None
            )
            if save: refProduct.save()

            # Parse GF
            try:
                self.parseProduct(list_product[5:-2])
            except RuntimeError as e:
                if not self.error_warning : self.stdout.write('Brand: %s' % self.caption.text)
                self.error_warning += 1
                self.stdout.write('\t'+red+'%s' % e+reset)
                self.stdout.write('\t%s' % list_product[5:-2])
            except RuntimeWarning as warnings:
                print_warning = False
                for warning in warnings.args[0]:
                    if warning[0] == 1:
                        continue
                    if print_warning == False:
                        print_warning = True
                        if not self.error_warning : self.stdout.write('Brand: %s' % self.caption.text)
                        self.error_warning += 1
                        self.stdout.write('\t%s' % list_product[5:-2])
                    self.stdout.write('\t'+yellow+'%s' % warning[1]+reset)
            except IndexError as e:
                try:
                    self.parseNote(list_product[5:-2])
                except RuntimeWarning as e:
                    if not self.error_warning : self.stdout.write('Brand: %s' % self.caption.text)
                    self.error_warning += 1
                    self.stdout.write('\t'+yellow+'%s' % e+reset)
                    self.stdout.write('\t%s' % list_note)
                if self.note != '':
                    note.append(self.note)

            if len(note) > 2:
                if not self.error_warning : self.stdout.write('Brand: %s' % self.caption.text)
                self.error_warning += 1
                self.stdout.write('\t'+red+'Too many notes %s' % note+reset)

            if len(note) == 2:
                try:
                    note_obj = Note.objects.get(note=note[0])
                except ObjectDoesNotExist as e:
                    note_obj = Note(note=note[0])
                    if save: note_obj.save()
                try:
                    category_obj = Category.objects.get(note=note[1])
                except ObjectDoesNotExist as e:
                    category_obj = Category(note=note[1])
                    if save: category_obj.save()
            if len(note) == 1:
                try:
                    category_obj = Category.objects.get(note=note[0])
                except ObjectDoesNotExist as e:
                    category_obj = Category(note=note[0])
                    if save: category_obj.save()

            if self.product is None:
                continue
            if save:
                gluten_free = Product (
                    description = self.product['name'],
                    unit = self.product['format'],
                    price = self.product['price'],
                    gluten_free = True,
                    company = company,
                    category = category_obj,
                    note = note_obj
                )
                gluten_free.save()

                association = Association (
                    equivalent = refProduct,
                    gluten_free = gluten_free
                )
                association.save()

            #if len(note) == 2:
            #    self.stdout.write('\tNote: %s' % note_obj.note)
            #    self.stdout.write('\tCategory: %s' % category_obj.note)

            # Clear all notes and categories
            note=[]

    def handle(self, **options):
        self.stdout.write('Loading file %s...' % options['html_file'])
        self.stdout.write('Save %s...' % options['save'])
        save = options['save']
        #save = True
        html = lxml.html.parse(options['html_file'])
        tables = html.findall(".//table")
        self.stdout.write('nb tables %s' % len(tables))
        for table in html.iterfind(".//table"):
            self.error_warning=0

            # First child must be a caption
            self.caption = table[0]

            # Next row: parse brand name, url, and date
            row = self.caption.getnext()
            if row[0].get('colspan') is not '5':
                 self.stdout.write('\tNot a brand table')
                 continue
            if row[1].get('colspan') is not '5':
                 self.stdout.write('\tNot a brand table')
                 continue

            # Parse Brand
            self.parseBrand(row[1])
            brand_note = None
            new_company = None
            if self.brand_note != []:
                brand_note = Note(note = '. '.join(self.brand_note))
                self.stdout.write("\tNote: %s" % brand_note.note)
                if save:
                    brand_note.save()
            if save:
                new_company = Company(  name=self.caption.text, 
                                        validation_date = self.date,
                                        note = brand_note,
                                        certification = ' / '.join(self.certification) )
                new_company.save()
            #new_company = Company.objects.get( name=self.caption.text )
            for name in self.brand_name.split('/'):
                if save:
                    brand = Brand(name=name.strip(), company=new_company)
                    brand.save()
            for url in self.url:
                url = url.strip('/')
                if save:
                    new_site = Site(domain=url, company=new_company)
                    new_site.save()

            # Next row must be for table header
            row = row.getnext()
            text = row.find("td").xpath("string()")
            if text != "Description":
                self.stdout.write(red+'Header table first column %s is not Description' % text+reset)

            # Parse products
            self.parseProducts(row, new_company, options['save'])

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('html_file', type=argparse.FileType('r'))
        # Named (optional) arguments
        parser.add_argument('-s', '--save',
            action='store_true',
            dest='save',
            default=False,
            help='Save to dbref database')
