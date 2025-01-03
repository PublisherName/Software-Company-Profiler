from urllib.parse import urljoin

import scrapy

from ..items import SoftwareCompanyProfilerItem


class TechbehemothsSpider(scrapy.Spider):
    name = "techbehemoths"
    allowed_domains = ["techbehemoths.com"]
    start_urls = []

    def __init__(self, url=None, output=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if url:
            self.start_urls = [url]
        else:
            raise ValueError("You must provide a --url argument to scrape.")
        self.output_file = output if output else "output.csv"

    def parse(self, response):
        """Parse the initial page and handle pagination."""
        try:
            total_pages = self.get_total_pages(response)
            self.logger.info(f"Total pages to scrape: {total_pages}")

            for page in range(1, total_pages + 1):
                next_page = f"{response.url.rstrip('/')}?page={page}"
                self.logger.info(f"Next Page url :  {next_page}")
                yield scrapy.Request(
                    next_page,
                    callback=self.parse_page,
                    errback=self.handle_error,
                    meta={"dont_retry": True},
                )
        except Exception as e:
            self.logger.error(f"Error during parsing: {e}")

    def parse_page(self, response):
        """Handle subsequent pages."""
        companies = response.css("article.co-box")
        if not companies:
            self.logger.warning(f"No companies found on {response.url}")
            return

        for company in companies:
            yield from self.parse_company(company, response.url)

    def parse_company(self, company_div, base_url):
        """Extract basic company info and follow profile links for detailed info."""

        name = company_div.css(".co-box__name a::text").get(default="").strip()
        profile_link = company_div.css("a.btn.btn-outlined.btn-black.highlight::attr(href)").get()
        profile_url = urljoin(base_url, profile_link) if profile_link else None

        if profile_url:
            yield scrapy.Request(
                profile_url,
                callback=self.parse_profile,
                errback=self.handle_error,
                meta={"dont_retry": True, "name": name},
            )

    @staticmethod
    def parse_profile(response):
        item = SoftwareCompanyProfilerItem()
        item["name"] = response.meta["name"]
        if item["name"]:
            item["address"] = (
                response.css('div[itemprop="address"] span[itemprop="streetAddress"]::text')
                .get(default="")
                .strip()
            )
            item["city"] = (
                response.css('div[itemprop="address"] span[itemprop="addressLocality"]::text')
                .get(default="")
                .strip()
            )

            item["phone"] = response.css('a[href^="tel:"] .val::text').get(default="").strip()
            item["website"] = (
                response.css('a:contains("Visit Website")::attr(href)')
                .get(default="")
                .split("?")[0]
            )

            item["email"] = response.css(".co-box__loc-itm::text").get(default="").strip()
            item["career_page"] = response.css(".co-box__loc-itm::text").get(default="").strip()
            item["linkedin"] = response.css(".co-box__loc-itm::text").get(default="").strip()

            yield item

    @staticmethod
    def get_total_pages(response):
        """Extract total number of pages."""
        pages = response.css(".pagination-box span.label::text").getall()
        return max((int(p) for p in pages if p.isdigit()), default=1)

    def handle_error(self, failure):
        """Handle request failures."""
        self.logger.error(f"Request failed: {failure.request.url}")
        self.logger.error(f"Error: {failure.value}")
