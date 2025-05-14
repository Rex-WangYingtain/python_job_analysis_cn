import scrapy
from spider.items import StockstarItem,StockstarItemLoader

class StockSpider(scrapy.Spider):
    name = 'stock'                                 #定义爬虫名称
    allowed_domains = ['quote.stockstar.com']    #定义爬虫域
    start_urls = ['https://quote.stockstar.com/stock/bjs_1_0_1.html']
    #定义开始爬虫链接
    def parse(self,response):    #撰写爬虫逻辑
        page = int(response.url.split("_")[-1].split(".")[0])  #抓取页码
        item_nodes = response.css('#datalist tr')
        for item_node in item_nodes:
            #根据item文件中所定义的字段内容，进行字段内容的抓取
            item_loader = StockstarItemLoader(item=StockstarItem(),selector= item_node)
            item_loader.add_css("code","td:nth-child(1) a::text")
            item_loader.add_css("abbr", "td:nth-child(2) a::text")
            item_loader.add_css("traded_market_value", "td:nth-child(3)::text")
            item_loader.add_css("aggregate_market_value", "td:nth-child(4)::text")
            item_loader.add_css("capital_stock_in_circulation", "td:nth-child(5)::text")
            item_loader.add_css("total_stock_issue", "td:nth-child(6)::text")
            stock_item = item_loader.load_item()
            yield stock_item
        if item_nodes:
            next_page = page + 1
            next_url = response.url.replace("{0}.html".format(page),"{0}.html".format(next_page))
            yield scrapy.Request(url=next_url,callback=self.parse)