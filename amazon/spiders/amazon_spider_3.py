# -*- coding: utf-8 -*-

import time
import scrapy
import selenium
from selenium import webdriver
from selenium.webdriver.firefox.webdriver import FirefoxProfile
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver import DesiredCapabilities
from amazon.items import AmazonItem
import re

class AmazonSpider(scrapy.Spider):
    num = 1
    pages = 100

#    start = (num - 1) * pages + 1
#    end = num * pages + 1
#     start = 0 + 1
    start = 34 + 1
    # end = 1000 + 1
    end = 35 + 1

    i = start

    name = 'amazon_3_' + str(num)

    def __init__(self):
        self.start_urls = ['https://www.amazon.com/review/top-reviewers?page=' + str(self.start)]
        self.allowed_domains = ['www.amazon.com']
        # self.profile = FirefoxProfile('/home/romitas/.mozilla/firefox/68h3udd9.AmazonScraper')
        binary = FirefoxBinary(firefox_path='/Applications/Firefox.app/Contents/MacOS/Firefox')
        profile = webdriver.FirefoxProfile()
        profile.set_preference('network.protocol-handler.external.mailto', False)
        # profile.add_extension(extension='/Applications/Firefox.app/Contents/Resources/browser/features/e10srollout@mozilla.org.xpi')
        firefox_capabilities = DesiredCapabilities.FIREFOX
        firefox_capabilities['marionette'] = True
        self.driver = webdriver.Firefox(firefox_profile=profile, firefox_binary=binary, capabilities=firefox_capabilities)

        self.driver_login()


    def parse(self, response):
        reviewers = response.xpath('//tr[contains(@id, "reviewer")]/td[3]/a')
        for reviewer in reviewers:
            name = reviewer.xpath('b/text()').extract()
            href = reviewer.xpath('@href').extract()
            rev_url = 'https://www.amazon.com' + href[0]
            self.driver.get(rev_url)

            eny_id = re.compile(r'.*\/profile\/(\w+)').search(rev_url).group(1)
            email_xpath = '//a[@id="/gp/profile/' + eny_id + '"]'
            see_more_xpath = '//span[contains(., "See more")]/..'
            send_email_xpath = '//a[contains(., "Send an Email")]'
            email = ''

            try:
                see_more_link = self.driver.find_element_by_xpath(see_more_xpath)
                see_more_link.click()
                email_link = self.driver.find_element_by_xpath(send_email_xpath)
                email_link.click()
                time.sleep(5)
            except:
                email = '-'

            sel = scrapy.Selector(text=self.driver.page_source)

            if email != '-':
                email = sel.xpath(email_xpath + '/text()').extract()[0]

            item = AmazonItem()
            item['name'] = name
            item['email'] = email
            item['idstr'] = eny_id
            yield item

        self.i += 1
        print 'let me sleep for a while ~~~~~~~~~~~~~~~~'
        time.sleep(10)

        if self.i <= self.end:
            yield scrapy.Request('https://www.amazon.com/review/top-reviewers?page=' + str(self.i), callback=self.parse)

    def driver_login(self):
        login_url = "https://www.amazon.com/ap/signin?_encoding=UTF8&openid.assoc_handle=usflex&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.mode=checkid_setup&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&openid.ns.pape=http%3A%2F%2Fspecs.openid.net%2Fextensions%2Fpape%2F1.0&openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.com%2Freview%2Ftop-reviewers%2F%3Fref_%3Dnav_signin"
        self.driver.get(login_url)

        login = self.driver.find_element_by_xpath('//input[@id="ap_email"]')
        password = self.driver.find_element_by_xpath('//input[@id="ap_password"]')

        submit = self.driver.find_element_by_xpath('//input[@id="signInSubmit"]')

        # Sure won't work this way.
        # In order to login you have to put your own Amazon email/password here
        login.send_keys('<email>')
        password.send_keys('<password>')
        submit.click()