import scrapy


class MlSpider(scrapy.Spider):
    name = 'ml'
    start_urls = ['https://www.mercadolivre.com.br/ofertas']

    def parse(self, response, **kwargs):
        for i in response.xpath('//li[@class="promotion-item"]'):
            price = i.xpath('.//span[@class="promotion-item__price"]//text()').getall()
            title = i.xpath('.//p[@class="promotion-item__title"]/text()').get()
            link = i.xpath('./a/@href').get()

            yield {
                'price' : price,
                'title' : title,
                'link' : link
            }