from scrapy import Spider, Request

class GreyboxSpider(Spider):
    name = "greybox"
    teams_dict = {}

    def start_requests(self):
        yield Request(
            url="https://statistiky.debatovani.cz/?page=tymy",
            callback=self.parse,
        )

    def parse(self, response):
        data = response.xpath("//tr/td/a[contains(@href, 'page=tym')]")

        for team in data:
            name = team.xpath("./text()").get()
            team_url = response.urljoin(team.xpath("./@href").get())
            team_id = int(team_url.split("tym_id=")[1])

            yield {
                "type": "team",
                "team_id": team_id,
                "team_name": name,
                "team_url": team_url,
            }

            self.teams_dict[team_id] = name

        yield Request(
            url="https://statistiky.debatovani.cz/?page=souteze",
            callback=self.parseCompetition,
        )

    def parseCompetition(self, response):
        data = response.xpath(
            "//tr/td/a[contains(@href, 'page=soutez') or contains(@href, 'page=liga')]"
        )

        for comp in data:
            comp_name = comp.xpath("./text()").get()
            comp_url = response.urljoin(comp.xpath("./@href").get())

            yield {
                "type": "competition",
                "competition_name": comp_name,
                "competition_url": comp_url,
            }

        yield Request(
            url="https://statistiky.debatovani.cz/?page=debaty",
            callback=self.parseDebates,
        )

    def parseDebates(self, response):
        debates = response.xpath("//tr[td/a[contains(text(), 'více')]]")

        for d in debates:
            more_url = response.urljoin(
                d.xpath(".//a[contains(text(), 'více')]/@href").get()
            )

            yield Request(
                url=more_url,
                callback=self.parseDebateDetail,
            )

        next_page = response.xpath("//a[contains(text(), 'Další')]/@href").get()
        if next_page:
            yield Request(
                url=response.urljoin(next_page),
                callback=self.parseDebates,
            )

    def parseDebateDetail(self, response):
        yield {
            "type": "debate",
            "debate_url": response.url,
            "date": response.xpath("//td[text()='Datum']/following-sibling::td/text()").get(),
            "motion": response.xpath("//td[text()='Téma']/following-sibling::td/text()").get(),
            "teams": response.xpath("//table//tr/td/text()").getall(),
        }
