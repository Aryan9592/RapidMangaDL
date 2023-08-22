from urllib.parse import urlparse
import requests


import sys
import os

from manga_dl.manga_sources.base_source import MangaInfo

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from selenium.webdriver.common.by import By


from tools.utils import logger, Driver
from tools.exceptions import MangaNotFound, InvalidMangaUrl
from bs4 import BeautifulSoup
from fake_headers import Headers
import re
from urllib.parse import quote_plus
from .base_source import BaseSource
from .utils import MangaInfo, Chapter, scraper, static_exists, exists


class MangaReader(BaseSource):
    domain = "mangareader.to"
    manga_format = "https://{domain}/{ID}"

    def __init__(self, url):
        super().__init__(url)
        self.use_selenium_in_get_chapter_img_urls = True
    
    @property
    def _id(self) -> str:
        parts = self.url.split("/")
        return parts[-1]
        
    @staticmethod
    @static_exists("https://mangareader.to/search?keyword=")
    def search(query: str) -> list[MangaInfo]:
        url = f"https://mangareader.to/search?keyword={quote_plus(query)}"
        results = []
        try:
            res = scraper.get(url)

            if res:
                soup = BeautifulSoup(res.text, "html.parser")
                manga_list = soup.find(class_ = 'manga_list-sbs')
                items = manga_list.select(".item") if manga_list else [] # type: ignore
                for item in items:
                    title: str = ""
                    url: str = ""
                    img: str = "/public/error.png"
                    
                    # Title and URL
                    poster = item.find(class_="manga-poster")
                    if poster:
                        url = poster['href'] # type: ignore 
                        imgt = poster.find("img") # type: ignore
                        if imgt:
                            img = imgt['src'] # type: ignore
                            title = imgt['alt'] # type: ignore
                    
                    if url.startswith("/"):
                        url = f"https://{domain}{url}" # type: ignore
                     
                    # last-chapter   
                    cht = item.find(class_="chapter")
                    last_chapter = ""
                    if cht:
                        link = cht.find("a")
                        if link:
                            alink = link["href"] #type: ignore
                            last_chapter = alink.split("/")[-1] #type: ignore
                    
                    m = MangaInfo(title=title, url=url)
                    m.cover_url = img
                    m.last_chapter = last_chapter
                    
                    results.append(m)
        
        except Exception as e:
            logger.error(f"Error searching for {query} in {MangaReader.domain}: {e}")

        return results
    
    @exists
    def get_info(self):
        try:
            res = scraper.get(self.url)
            soup = BeautifulSoup(res.text, "html.parser")


        except Exception as e:
            logger.error(f"Error")