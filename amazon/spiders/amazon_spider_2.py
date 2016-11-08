# -*- coding: utf-8 -*-

import time
import scrapy
import selenium
from selenium import webdriver
# from selenium.webdriver.firefox.webdriver import FirefoxProfile
from amazon.items import AmazonItem
from selenium.webdriver.chrome.options import Options
import urllib2
import cookielib
import re

class AmazonSpider(scrapy.Spider):
    num = 1
    pages = 100

#    start = (num - 1) * pages + 1
#    end = num * pages + 1
    start = 0 + 1
    end = 1000 + 1

    i = start



    name = 'amazon_t_' + str(num)

    def __init__(self):
        cookie_file_name = 'cookie.txt'
        self.cookie = cookielib.MozillaCookieJar(cookie_file_name)

        self.start_urls = ['http://www.amazon.com/review/top-reviewers?page=' + str(self.start)]
        self.allowed_domains = ['www.amazon.com']
        #        self.profile = FirefoxProfile('/home/romitas/.mozilla/firefox/68h3udd9.AmazonScraper')
        # profile = FirefoxProfile()
        # profile.set_preference('network.protocol-handler.external.mailto', False)
        # self.driver = webdriver.Firefox(self.profile)

        driver_location = "/Users/mac/bin/chromedriver"
        options = webdriver.ChromeOptions()
        options.add_argument('--lang=es')
        self.driver = webdriver.Chrome(executable_path=driver_location, chrome_options=options)
        self.driver_login()


    def parse(self, response):
        #// *[ @ id = "reviewer1"] / td[3] / a
        for reviewer in response.xpath('//tr[contains(@id, "reviewer1")]/td[3]/a'):
            name = reviewer.xpath('b/text()').extract()
            href = reviewer.xpath('@href').extract()

            rev_url = 'http://www.amazon.com' + href[0]

            self.driver.get(rev_url)
            rev_id = rev_url.split('/')[-1]
            if rev_id == '':
                rev_id = response.url.split('/')[-2]

            usr_xpath = '//a[@id="/gp/profile/' + rev_id + '"]'
            see_more_xpath = '//a[@class="a-declarative"]'
            # email_xpath = '//*[@id="a-page"]/div[2]/div/div[1]/div/div/div/div[2]/div/div[2]/div/div/div[2]/div/div/div[1]/div[2]/a'

            email_xpath = '//span[contains(@class, "a-size-small a-color-link break-word pr-show-email")]'
            email = ''

            # save cookie
            self.cookie.save(ignore_discard=True, ignore_expires=True)

            #// *[ @ id = "a-page"] / div[2] / div / div[1] / div / div / div / div[2] / div / div[1] / div / span
            #//span[contains(@class, "public-name-text")]

            try:
                eny_id = re.compile(r'.*\/profile\/(\w+)').search(rev_url).group(1)
                email_attempt = self.email_fetch(eny_id)
                print 'email_attempt@@@@@@@@@@@: ' + email_attempt
            except:
                email = '-'


            # /gp/profile/A1WPFIZ8P3O86V
            sel = scrapy.Selector(text=self.driver.page_source)

            if email != '-':
                email = sel.xpath(usr_xpath + '/text()').extract()[0]

            item = AmazonItem()
            item['name'] = name
            item['email'] = email

            yield item

        self.i += 1
        if self.i <= self.end:
            yield scrapy.Request('http://www.amazon.com/review/top-reviewers?page=' + str(self.i), callback=self.parse)

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


    def parse_reviewer(self):
        time.sleep(5)
        cur_url = self.driver.current_url
        rev_id = cur_url.split('/')[-1]
        if rev_id == '':
            rev_id = response.url.split('/')[-2]

        email_xpath = '//a[@id="/gp/profile/' + rev_id + '"]'

        email_link = self.driver.find_element_by_xpath(email_xpath)
        email_link.click()

        sel = scrapy.Selector(text=driver.page_source)

        email = sel.xpath(email_xpath + '/text()').extract()[0]
        name  = sel.xpath('//h1/text()').extract()[0]

        item = Amazon.Item()
        item['name'] = name
        item['email'] = email

        yield item

    def email_fetch(self, eny_id):
        email = '-'

        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookie))
        url = 'https://www.amazon.com/gp/profile/'+eny_id+'/customer_email'
        print 'rev_id=========: ' + eny_id + ', url**********: ' + url
        result = opener.open(url)
        if result['status'] == 'ok':
            email = result['data']['email']

        return email