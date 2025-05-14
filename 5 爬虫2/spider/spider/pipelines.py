import pymysql
from pymysql import cursors
from scrapy.exceptions import DropItem

class StockstarPipeline:
    def __init__(self, host, port, user, password, db):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.db = db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            host=crawler.settings.get('MYSQL_HOST'),
            port=crawler.settings.get('MYSQL_PORT'),
            user=crawler.settings.get('MYSQL_USER'),
            password=crawler.settings.get('MYSQL_PASSWORD'),
            db=crawler.settings.get('MYSQL_DB'),
        )

    def open_spider(self, spider):
        # 初始化数据库连接
        self.connection = pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            db=self.db,
            charset='utf8mb4',
            cursorclass=cursors.DictCursor
        )
        self.cursor = self.connection.cursor()

    def close_spider(self, spider):
        # 关闭数据库连接
        self.connection.close()

    def process_item(self, item, spider):
        # 插入数据到数据库
        try:
            sql = '''
                INSERT INTO stock_bza (code, abbr, traded_market_value, aggregate_market_value, capital_stock_in_circulation, total_stock_issue)
                VALUES (%s, %s, %s, %s, %s, %s)
            '''
            self.cursor.execute(sql, (
                item['code'],
                item['abbr'],
                item['traded_market_value'],
                item['aggregate_market_value'],
                item['capital_stock_in_circulation'],
                item['total_stock_issue']
            ))
            self.connection.commit()
        except Exception as e:
            spider.logger.error(f"Error inserting item into MySQL: {e}")
            self.connection.rollback()
            raise DropItem(f"Failed to insert item into MySQL: {item}")

        return item