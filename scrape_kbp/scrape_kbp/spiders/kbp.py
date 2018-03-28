# -*- coding: utf-8 -*-
import scrapy
import pickle
import re
from html.parser import HTMLParser
import lxml
from io import BytesIO
from scrapy.utils.markup import remove_tags


class KbpSpiderSpider(scrapy.Spider):
    name = 'kbp_spider'
    start_urls = [
        'http://killedbypolice.net/kbp2015'
    ]

    def parse(self, response):
        # with open('kbp.xml', 'wb') as data_file:
        #     parser = lxml.etree.HTMLParser(recover=True)
        #     tree = lxml.etree.parse(BytesIO(response.body), parser)
        #     tree.write(data_file)

        clean_body = self.get_data(response)
        response = response.replace(body=clean_body)

        people = self.manage_data(response)
        # people = self.normalize_data(people)
        # people = self.clean_data(people)

    def get_data(self, response):
        clean_response = bytes()
        with open('kbp.html', 'wb') as data_file:
            # with open('kbp.pickle', 'wb') as data_file:
            rows = re.split('<tr>', response.body.decode(
                'utf-8'), flags=re.IGNORECASE)

            for row in rows:
                text = row.replace('<center>', '')
                clean_row = lxml.html.fromstring(text)
                clean_row = lxml.html.tostring(clean_row)

                clean_response += clean_row

            # pickle.dump(data, data_file, protocol=0)
            data_file.write(clean_response)
            return clean_response
        #   with open('kbp.pickle', 'rb') as data_file:
        #     data2 = pickle.load(data_file)
        #     if data == data2:
        #         print('the data is the same')
        #     else:
        #         print('the data is different')

    def manage_data(self, response):

        people = []
        count = 0
        for row in response.css('div'):

            date_killed = row.css('div')[0].extract()
            if self.is_real_data(date_killed):
                count += 1

                person = row.extract().split('<td>')
                size = self.check_size(person)
                if size > 1:
                    self.split_data(row)
                else:
                    self.organize_single_data(row)
        print(count)

    # def organize_multiple_data(self, row):

    def organize_single_data(self, row):
        date_killed = row.css('td')[0].extract()
        date_killed = re.sub(
            r'\(.+\)', '', remove_tags(date_killed)).strip()

        state = remove_tags(row.css('td')[1].extract())
        gender_race = remove_tags(row.css('td')[2].extract())
        gender = None
        race = None
        if '/' in gender_race:
            gender_race = gender_race.split('/')
            gender = gender_race[0]
            race = gender_race[1]
        else:
            gender = gender_race

        photo = row.css('td')[3].css('a')

        if photo:
            photo = photo.css('a::attr(href)').extract_first()

        name_age = remove_tags(row.css('td')[3].extract()).split(',')

        name = name_age[0]
        age = None

        if len(name_age) == 2:
            age = re.search(r'\d+', name_age[1]).group()

        killed_by = list(remove_tags(row.css('td')[4].extract()).strip())

        kbp_links = []

        for link in row.css('td')[5].css('a::attr(href)').extract():
            kbp_links.append(link)

        news_links = []

        for link in row.css('td')[6].css('a::attr(href)').extract():
            news_links.append(link)

        return {
            'date_killed': date_killed,
            'state': state,
            'name': name,
            'age': age,
            'race': race,
            'gender': gender,
            'killed_by': killed_by,
            'kbp_links': kbp_links,
            'news_links': news_links
        }

    def normalize_data(self, people):
        data = []

        for person in people:
            if self.is_real_data(person):
                size = self.check_size(person)
            # date_killed, state, gender_race, name_age, killed_by, kbp_link, news_link = person

                if size > 1:
                    split_data = self.split_data(person)
                    data.extend(split_data)
                else:
                    data.append(person)
        return data

    def is_real_data(self, date_killed):
        months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun',
                  'jul', 'aug', 'sep', 'oct', 'nov', 'dec']

        date = date_killed.lower()

        if any(month in date for month in months) and not '<b>' in date:
            return True

        else:
            return False

    def check_size(self, person):
        size = 0

        # Check date field for more than one entry
        if size < person[0].count('<br>'):
            size = person[0].count('<br>')

        # Check name field for more than one entry
        if size < person[3].count('<br>'):
            size = person[3].count('<br>')

        if size > 0:
            return size + 1
        else:
            return 1

    def split_data(self, row):
        data = []
        people = row.extract().split('<td>')
        people.pop(0)
        # date_killed, state, gender_race, name_age, killed_by, kbp_link, news_link = person

        date_killed = re.split('<br>', people[0], flags=re.IGNORECASE)[0]
        state = remove_tags(
            re.split('<br>', people[1], flags=re.IGNORECASE)[0])
        gender_race_list = re.split('<br>', people[2], flags=re.IGNORECASE)
        name_age_list = re.split('<br>', people[3], flags=re.IGNORECASE)

        weapons = re.split('<br>', people[4], flags=re.IGNORECASE)
        weapons = list(map(lambda weapon: remove_tags(weapon), weapons))
        killed_by = list(set(weapons))
        links = row.css('td')[5].extract()
        htmlparser = LinksExtractor()
        htmlparser.feed(links)
        htmlparser.close()

        kbp_links = htmlparser.get_links()

        links = row.css('td')[6].extract()
        htmlparser.feed(links)
        htmlparser.close()

        news_links = htmlparser.get_links()

        # for i in range(0, len(gender_race_list) - 1):
        #     new_person = (
        #         date_killed, state, gender_race_list[i], name_age_list[i], killed_by, kbp_link, news_link)
        #     data.append(new_person)
        # return data

    def clean_data(self, people):
        # TAG_RE = re.compile(r'<[^>]+>')
        # parser = MyHTMLParser()
        for person in people:

            date_killed, state, gender_race, name_age, killed_by, kbp_link, news_link = person

            # parser.feed(date_killed)
            # date_killed = parser.handle_data(date_killed)
            # print(date_killed)
            # date_killed = TAG_RE.sub('', date_killed)
            # state = TAG_RE.sub('', state)
            # gender_race = re.split('\/', name_age, flags=re.IGNORECASE)
            # gender = gender_race[0]
            # race = gender_race[1]
            # picture = None
            # if 'href' in name_age:


class LinksExtractor(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.links = []
    # def start_a(self, attrs):
    #     if len(attrs) > 0:
    #         for attr in attrs:
    #             if attr[0] == "href":
    #                 self.links.append(attr[1])

    def get_links(self):
        return self.links

    def handle_starttag(self, tag, attrs):
        if len(attrs) > 0:
            for attr in attrs:
                if attr[0] == "href":
                    self.links.append(attr[1])
