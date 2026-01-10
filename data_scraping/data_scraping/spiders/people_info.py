from scrapy import Spider, Request

class PeopleSpider(Spider):
    name = "people"

    def start(self):
        yield Request(
            url="https://statistiky.debatovani.cz/?page=lide",
            callback=self.parse,
        )

    def parse(self, response):
        data = response.xpath("//table/tr[position()>1]")
        for person in data:
            person_id = person.xpath("/td/a/@href").get()[-4:]
            name = person.xpath("/td/a/text()").get()
            yield Request(
                url=f"https://statistiky.debatovani.cz/?page=clovek.debaty&clovek_id={person_id}",
                callback=self.parseFirst,
                meta={'person_id': person_id, 'name': name},
            )
    def parseFirst(self, response):
        data = response.xpath("//table/tr[position()>1]")
        last = data[-1]
        date = last.xpath("/td/text()").get()
        name = response.meta['name']
        person_id = response.meta['person_id']
        yield {
            name=name,
            date=date,
            person_id=person_id,
        }
            
