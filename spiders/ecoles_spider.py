#!/usr/bin/python
# -*- coding: utf-8 -*-

import scrapy
import time


class QuotesSpider(scrapy.Spider):
    name = "ecoles"

    def start_requests(self):
        urls = [
            'http://www.education.gouv.fr/pid24302/annuaire-resultat-recherche.html?ecole=1&lycee_name=&ville_name=&localisation=2&dept_select[]=76&public=1'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        ecoles = response.css('div.annuaire-etablissement-label')

        for ecole in ecoles:
            link = ecole.css('a::attr(href)').extract_first()
            if link is not None:
                link = response.urljoin(link)
                yield scrapy.Request(link, callback=self.parse_school)

        next_page = response.css('.annuaire-pagination li:nth-last-child(2) a')
        
        if next_page.css('img') is not None:
            next_page = next_page.css('::attr(href)').extract_first()

            if len(next_page) > 0:
                next_page = response.urljoin(next_page)
                yield scrapy.Request(next_page, callback=self.parse)


    def parse_school(self, response):
        
        details = response.css('div.annuaire-etablissement-fiche')

        if details is not None:
            # Clean code
            message = 'Code école : '.decode('utf8')
            code = details.css('span.annuaire-code::text').extract_first().replace(message,'')

            # Clean number
            message = ' Élèves'.decode('utf8')
            childrens = details.css('span.annuaire-nb-eleves::text').extract_first().replace(message,'')

            # Clean title
            message = 'École primaire publique '.decode('utf8')
            title = details.css('h2 span::text').extract_first().replace(message, '')

            # Type
            schoolType = details.css('div.fiche-type-etab::text').extract_first(),
            isMaternelle = 'maternelle' in str(schoolType)
            isPrimaire = 'entaire' in str(schoolType)

            # Public
            public = details.css('span.annuaire-type-etab::text').extract_first(),
            isPublic = 'publique' in str(public)
            
            # Address
            addr = details.css('p.annuaire-etablissement-infos-part3::text').extract()
            address = addr[0].replace('\n','')
            cityLine = addr[1].split(' ')
            postalCode = cityLine[0]
            city = addr[1].replace(postalCode + ' ', '')
            phone = addr[3]

            result = {
                'maternelle': isMaternelle,
                'primaire'  : isPrimaire, 
                'title'     : title,
                'childrens' : childrens,
                'public'    : isPublic,
                'code'      : code,
                'address'   : address,
                'postalCode': postalCode,
                'city'      : city,
                'phone'     : phone,
            }
            yield result


                


