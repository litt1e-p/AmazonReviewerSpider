# -*- coding: utf-8 -*-

import time
import scrapy
import selenium
from selenium import webdriver
# from selenium.webdriver.firefox.webdriver import FirefoxProfile
from amazon.items import AmazonItem
from selenium.webdriver.chrome.options import Options

class AmazonSpider(scrapy.Spider):

    name = 'amazon_my'

    def __init__(self):
        self.start_urls = ['https://www.amazon.com/gp/profile/A1QY67C9IW5ZPI?ie=UTF8&ref_=sv_ys_3']
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

        # email_xpath = '//a[@id="/gp/profile/' + rev_id + '"]'
        # email_xpath = '//*[@id="a-page"]/div[2]/div/div[1]/div/div/div/div[2]/div/div[2]/div/div/div[2]/div/div/div[1]/div[2]/a/span'
        # email_xpath = '//span[contains(@class, "a-size-small a-color-link break-word pr-show-email")]'
        # email_a_xpath = '//a[@class＝"a-declarative"]'
        email_xpath = '//span[contains(@class, "a-size-small a-color-link break-word pr-show-email")]'
        email = ''
        name_xpath = '//span[contains(@class, "public-name-text")]'
        name = ''

        try:
            email = response.xpath(email_xpath)
        except:
            email = '-'

        sel = scrapy.Selector(text=self.driver.page_source)
        if email != '-':
            email = sel.xpath(email_xpath + '/text()').extract()[0]

        try:
            name = sel.xpath(name_xpath)
        except:
            name = '*'
        if name != '*':
            name = sel.xpath(name_xpath + '/text()').extract()[0]

        item = AmazonItem()
        item['name'] = name
        item['email'] = email

        yield item

    def driver_login(self):
        login_url = "https://www.amazon.com/ap/signin?_encoding=UTF8&openid.assoc_handle=usflex&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.mode=checkid_setup&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&openid.ns.pape=http%3A%2F%2Fspecs.openid.net%2Fextensions%2Fpape%2F1.0&openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.com%2Fgp%2Fprofile%2FA1QY67C9IW5ZPI%3Fie%3DUTF8%26ref_%3Dsv_ys_3"
        self.driver.get(login_url)

        login = self.driver.find_element_by_xpath('//input[@id="ap_email"]')
        password = self.driver.find_element_by_xpath('//input[@id="ap_password"]')

        submit = self.driver.find_element_by_xpath('//input[@id="signInSubmit"]')

        # Sure won't work this way.
        # In order to login you have to put your own Amazon email/password here
        login.send_keys('<email>')
        password.send_keys('<password>')
        submit.click()
