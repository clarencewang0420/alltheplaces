import html
import json

import scrapy

from locations.dict_parser import DictParser


class BestWesternSpider(scrapy.spiders.SitemapSpider):
    name = "bestwestern"
    brands = [
        ("Best Western Premier", "Q830334"),
        ("Best Western Plus", "Q830334"),
        ("Aiden by Best Western", "Q830334"),
        ("Sure Hotel", "Q830334"),
        ("Surestay Plus", "Q830334"),
        ("Surestay", "Q830334"),
        ("Best Western", "Q830334"),
    ]
    allowed_domains = ["bestwestern.com"]
    sitemap_urls = ["https://www.bestwestern.com/etc/seo/bestwestern/hotels.xml"]
    sitemap_rules = [(r"en_US/book/.*\.html", "parse_hotel")]
    download_delay = 2.0
    custom_settings = {"ROBOTSTXT_OBEY": False}

    def parse_hotel(self, response):
        hotel_details = response.xpath('//div[@id="hotel-details-info"]/@data-hoteldetails').get()

        if not hotel_details:
            return

        hotel = json.loads(html.unescape(hotel_details))
        summary = hotel["summary"]
        for brand in self.brands:
            if summary["name"].lower().startswith(brand[0].lower()):
                item = DictParser.parse(summary)
                item["brand"], item["brand_wikidata"] = brand
                item["street_address"] = summary["address1"]
                item["website"] = response.url
                item["ref"] = summary["resort"]
                try:
                    # It's a big hotel chain, worth a bit of work to get the imagery.
                    image_path = hotel["imageCatalog"]["Media"][0]["ImagePath"]
                    item["image"] = "https://images.bestwestern.com/bwi/brochures/{}/photos/1024/{}".format(
                        summary["resort"], image_path
                    )
                except IndexError:
                    pass
                yield item
                return
