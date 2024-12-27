import json
from urllib.parse import urljoin

import scrapy

from ..items import NepalypScraperItem


class NepalypSpider(scrapy.Spider):
    name = "nepalyp"
    allowed_domains = ["www.nepalyp.com"]
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
                next_page = f"{response.url.rstrip('/')}/{page}"
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
        companies = response.css("div.company")
        if not companies:
            self.logger.warning(f"No companies found on {response.url}")
            return

        for company in companies:
            yield from self.parse_company(company, response.url)

    def parse_company(self, company_div, base_url):
        """Extract basic company info and follow profile links for detailed info."""
        header = company_div.css("div.company_header")
        name = header.css("h4 a::text").get(default="").strip()
        profile_link = header.css("h4 a::attr(href)").get()
        profile_url = urljoin(base_url, profile_link) if profile_link else None

        if profile_url:
            yield scrapy.Request(
                profile_url,
                callback=self.parse_profile,
                errback=self.handle_error,
                meta={"dont_retry": True, "name": name},
            )

    def parse_profile(self, response):
        """Extract detailed company information from the profile page."""
        item = NepalypScraperItem()
        item["name"] = response.meta.get("name", "")
        json_ld = response.css('script[type="application/ld+json"]::text').get()

        if json_ld:
            try:
                data = json.loads(json_ld)
                item["address"] = data.get("address", {}).get("streetAddress", "")
                item["city"] = data.get("address", {}).get("addressLocality", "")
                item["phone"] = data.get("telephone", "")
                item["website"] = data.get("url", "")
                item["career_page"] = data.get("career_page", "")
                item["linkedin"] = data.get("linkedIn", "")
            except json.JSONDecodeError:
                self.logger.error(f"Error parsing JSON-LD on {response.url}")

        yield item

    def handle_error(self, failure):
        """Handle request failures."""
        self.logger.error(f"Request failed: {failure.request.url}")
        self.logger.error(f"Error: {failure.value}")

    @staticmethod
    def get_total_pages(response):
        """Extract total number of pages."""
        pages = response.css("div.pages_container a.pages_no::text").getall()
        return max((int(p) for p in pages if p.isdigit()), default=1)
