#!/usr/bin/python
# -*- coding: utf-8 -*-

import scrapy
import time
import sys
import json

posteTypeList = {}
posteList = {}

class QuotesSpider(scrapy.Spider):
    name = "postes"

    def start_requests(self):
        urls = [
            'https://un-bon-crawler-ne-donne-jamais-ses-sources.gouv.fr?SESSION_ID=tutu'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):

        posteTypes = response.css('select[name=nature]')

        for posteType in posteTypes.css('option') :

            code = posteType.css('::attr(value)').extract_first()
            description = posteType.css('::text').extract_first()

            if code == '*':
                continue

            posteTypeList[code] = description

            formdata = {
                "action": "SUITE",
                "inature": description.replace(' ', '+'),
                "vac": "*",
                "zon": "*",
                "nat": code,
                "specialite": "*"
            }

            url = 'https://un-bon-crawler-ne-donne-jamais-ses-sources.gouv.fr?SESSION_ID=tutu'

            print code

            request = scrapy.FormRequest(url = url, callback=self.parsePoste, formdata=formdata, meta={'code': code})

            yield request


    def parsePoste(self, response):

        code = response.meta.get('code')

        table = response.css('center table tr')

        i = 0

        postes = []

        for tr in table:

            poste = {}

            i = i + 1

            # First line is header and that useless
            if i == 1:
                continue

            td = tr.css('td')

            poste['num'] = td[1].css('::text').extract_first()
            poste['area_type'] = td[2].css('::text').extract_first()
            poste['name'] = td[3].css('::text').extract_first()
            poste['type'] = td[4].css('::text').extract_first()
            poste['specialty'] = td[5].css('::text').extract_first()
            poste['available'] = td[6].css('::text').extract_first()
            poste['maybe_available'] = td[7].css('::text').extract_first()
            poste['bloqued'] = td[8].css('::text').extract_first()
            poste['quotity'] = td[9].css('::text').extract_first()
            poste['fulltime'] = td[10].css('::text').extract_first()

            postes.append(poste)

        print code + ': done'

        yield { code: postes }
