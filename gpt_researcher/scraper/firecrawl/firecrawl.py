from bs4 import BeautifulSoup
import os
from gpt_researcher.scraper.utils import get_relevant_images
from gpt_researcher.utils.logger import get_formatted_logger
import requests
from threading import Semaphore

logger = get_formatted_logger()
guard = Semaphore(4)

class FireCrawl:

    def __init__(self, link: str, session: requests.Session | None = None):
        self.link = link
        self.session = session or requests.Session()
        import firecrawl
        self.firecrawl = firecrawl.Firecrawl(api_key=self.get_api_key(), api_url=self.get_server_url())
        self.firecrawl_scrape_images: bool = os.environ.get("FIRECRAWL_SCRAPE_IMAGES", "false").lower().strip() in "true1yes"

    def get_api_key(self) -> str:
        """
        Gets the FireCrawl API key
        Returns:
        Api key (str)
        """
        try:
            api_key = os.environ["FIRECRAWL_API_KEY"]
        except KeyError:
            raise Exception(
                "FireCrawl API key not found. Please set the FIRECRAWL_API_KEY environment variable.")
        return api_key

    def get_server_url(self) -> str:
        """
        Gets the FireCrawl server URL.
        Default to official FireCrawl server ('https://api.firecrawl.dev').
        Returns:
        server url (str)
        """
        try:
            server_url = os.environ["FIRECRAWL_SERVER_URL"]
        except KeyError:
            server_url = 'https://api.firecrawl.dev'
        return server_url

    def scrape(self) -> tuple:
        """
        This function extracts content and title from a specified link using the FireCrawl Python SDK,
        images from the link are extracted using the functions from `gpt_researcher/scraper/utils.py`.

        Returns:
          The `scrape` method returns a tuple containing the extracted content, a list of image URLs, and
        the title of the webpage specified by the `self.link` attribute. It uses the FireCrawl Python SDK to
        extract and clean content from the webpage. If any exception occurs during the process, an error
        message is printed and an empty result is returned.
        """

        try:
            with guard:
                response = self.firecrawl.scrape(
                    url=self.link, 
                    formats=["markdown"],
                    block_ads=True
                )

            if response.metadata.status_code != 200 or response.metadata.error is not None:
                logger.error(f"Scrape failed! : {response.metadata.error}; Status code: {response.metadata.status_code}")
                return "", [], ""

            content = response.markdown
            title = response.metadata.title
            relevant_image_urls = []

            if self.firecrawl_scrape_images:
                response_bs = self.session.get(self.link, timeout=4)
                soup = BeautifulSoup(response.html, "lxml", from_encoding=response_bs.encoding)
                relevant_image_urls = get_relevant_images(soup, self.link)

            return content, relevant_image_urls, title

        except Exception as e:
            logger.error("Error! : " + str(e))
            return "", [], ""
