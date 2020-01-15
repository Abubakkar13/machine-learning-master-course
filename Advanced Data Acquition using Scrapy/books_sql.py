# -*- coding: utf-8 -*-

# Rename File to books.py

from scrapy import Spider
from scrapy.http import Request
import os
import glob
import csv
import MySQLdb

def product_info(response, value):
	return response.xpath('//th[text()="' + value + '"]/following-sibling::td/text()').extract_first()


class BooksSpider(Spider):
	name = 'books'
	allowed_domains = ['books.toscrape.com']
	start_urls = ['http://books.toscrape.com']

	def parse(self, response):
		books = response.xpath('//h3/a/@href').extract()
		for book in books:
			absolute_url = response.urljoin(book)
			yield Request(absolute_url, callback=self.parse_book)

	def parse_book(self, response):
		title = response.css('h1::text').extract_first()
		rating = response.xpath('//*[contains(@class, "star-rating")]/@class').extract_first()
		upc = product_info(response, 'UPC')
		product_type = product_info(response, 'Product Type')
		yield {
			'title' : title,
			'Rating' : rating,
			'UPC' : upc,
			'Product Type' : product_type,
		}

	def close(self, reason):
		csv_file = max(glob.iglob('*.csv'), key=os.path.getctime)
		mydb = pymysql.connect(host='localhost', user='root', passwd='', db='books_database')
		cursor = mydb.cursor()
		csv_data = csv.reader(open(csv_file))
		print(csv_data)

		row_count=0
		for row in csv_data:
			if row_count!=0:
				cursor.execute('INSERT IGNORE INTO books_table(title, rating, UPC, product_type) VALUES(%s, %s, %s, %s)', row)
				row_count+=1

		mydb.commit()
		cursor.close()

