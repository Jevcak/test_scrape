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
                "id": team_id,
                "name": name,
                "url": team_url,
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
        # TODO:
        # u kazdeho yieldu bych si vyparsoval i id souteze, jako je to u tymu
        for comp in data:
            comp_name = comp.xpath("./text()").get()
            comp_url = response.urljoin(comp.xpath("./@href").get())

            yield {
                "type": "competition",
                "name": comp_name,
                "url": comp_url,
            }

        yield Request(
            url="https://statistiky.debatovani.cz/?page=debaty",
            callback=self.parseDebates,
        )

    def parseDebates(self, response):
        debates = response.xpath("//tr[td/a[contains(text(), 'více')]]")
        # tohle nevypada dobre ale fungovat to asi bude
        for d in debates:
            more_url = response.urljoin(
                d.xpath(".//a[contains(text(), 'více')]/@href").get()
                # tohle by snad melo fungovat
            )

            yield Request(
                url=more_url,
                callback=self.parseDebateDetail,
            )

        next_page = response.xpath("//a[contains(text(), 'Další')]/@href").get()
        # kde si nasel nejakou next page
        # tady zadny nextpage neni https://statistiky.debatovani.cz/?page=debaty
        if next_page:
            yield Request(
                url=response.urljoin(next_page),
                callback=self.parseDebates,
            )

    def parseDebateDetail(self, response):
        yield {
            "type": "debate",
            "url": response.url,
            "date": response.xpath("//td[text()='Datum']/following-sibling::td/text()").get(),
            "motion": response.xpath("//td[text()='Téma']/following-sibling::td/text()").get(),
            "teams": response.xpath("//table//tr/td/text()").getall(),
            # TODO:
            # asi by mi prislo rozumejsi brat ids teamu nez nazvy, 
            # navic ten xpath se mi zda ze bere vsechny polozky v tabulce,
            # nejen nazev teamu, kdyz se podivas co vsechno v ty tabulce splnuje 
            # ten tvuj xpath> view-source:https://statistiky.debatovani.cz/?page=debata&debata_id=11370
            # zrovna v tomhle linku ti nebude fungovat ani tema, datum, 
            # takze to chce najit jinej filtr
        }
