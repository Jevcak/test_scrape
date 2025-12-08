from scrapy import Spider, Request

class GreyboxSpider(Spider):
    name = "greybox"
    teams_dict = {}
    async def start(self):
        url = "https://statistiky.debatovani.cz/?page=tymy"
        yield Request(
            url=url,
            callback=self.parse,
            # headers = {
            #     'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            #     'accept-language': 'cs-CZ,cs;q=0.9,en;q=0.8,de;q=0.7',
            #     'cache-control': 'no-cache',
            #     'pragma': 'no-cache',
            #     'priority': 'u=0, i',
            #     'referer': 'https://statistiky.debatovani.cz/',
            #     'sec-ch-ua': '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
            #     'sec-ch-ua-mobile': '?0',
            #     'sec-ch-ua-platform': '"Windows"',
            #     'sec-fetch-dest': 'document',
            #     'sec-fetch-mode': 'navigate',
            #     'sec-fetch-site': 'same-origin',
            #     'sec-fetch-user': '?1',
            #     'upgrade-insecure-requests': '1',
            #     'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
            #     # 'cookie': 'PHPSESSID=frh05lfdlc7u6raocp43bnp9vr',
            # },
        )

    async def parse(self, response):
        data = response.xpath("//tr/td/a[contains(@href, 'page=tym')]")
        for team in data:
            name = team.xpath("./text()").get()
            team_url = team.xpath("./@href").get()
            team_id = int(team_url.split("tym_id=")[1])
            yield {
                'team_id': team_id,
                'team_url': team_url,
                'team_name': name,
            }
            self.teams_dict[team_id]=name
        yield Request(
            url = "https://statistiky.debatovani.cz/?page=souteze",
            callback=self.parseCompetition,
            headers = {
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'accept-language': 'cs-CZ,cs;q=0.9,en;q=0.8,de;q=0.7',
                'cache-control': 'no-cache',
                'pragma': 'no-cache',
                'priority': 'u=0, i',
                'referer': 'https://statistiky.debatovani.cz/?page=tymy',
                'sec-ch-ua': '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
                # 'cookie': 'PHPSESSID=frh05lfdlc7u6raocp43bnp9vr',
            },
        )
    def parseCompetition(self, response):
        data = response.xpath("//tr/td/a[contains(@href, 'page=soutez') or contains(@href, 'page=liga')]")
        for comp in data:
            comp_url = comp.xpath("./@href").get()
            # TODO: tady request pres vsechny ligy/souteze
        yield Request(
            url="https://statistiky.debatovani.cz/?page=debaty",
            callback=self.parseDebates,
        )
        pass
    def parseDebates(self, response):
        print('Debates')
