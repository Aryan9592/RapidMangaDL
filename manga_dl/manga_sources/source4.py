from urllib.parse import urlparse
import requests


import sys
import os

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
        url = MangaReader.valid_url(url)
        super().__init__(url)
        self.headers["Referer"] = f"https://{self.domain}/"
    
    @property
    def _id(self) -> str:
        url = self.url
        if self.url.endswith("/"):
            url = self.url[:-1]
        return url.split("/")[-1]
    
    @staticmethod
    def valid_url(url: str) -> str:
        parse = urlparse(url)
        parts = parse.path.replace("//", "/").split("/")[1:]

        if len(parts) == 1:
            return url
        elif len(parts) > 1:
            return f"{parse.scheme}://{parse.netloc}/{parts[0]}"
        else:
            raise InvalidMangaUrl(f"Invalid url: {url}")
        
    @staticmethod
    @static_exists("https://mangareader.to/search")
    def search(query: str) -> list[MangaInfo]:
        url = "https://mangareader.to/search?keyword=" + quote_plus(query)
        
        results = []
        try:
            res = scraper.get(url)
            if res:
                soup = BeautifulSoup(res.text, "html.parser")
                manga_list = soup.find(class_ = 'manga_list-sbs')
                if not manga_list:
                    raise Exception("No results found")
                
                items = manga_list.select(".item") #type: ignore
                
                for item in items:
                    poster = item.find(class_="manga-poster")
                    
                    # cover, link
                    if poster:
                        alink = poster['href'] # type: ignore 
                        if alink.startswith("/"): # type: ignore
                            link = f"https://{MangaReader.domain}{alink}"
                        else:
                            link = alink
                        imgt = poster.find("img") # type: ignore
                        if imgt:
                            cover = imgt["src"] # type: ignore
                    
                    # titel
                    title_name = item.find(class_="manga-name")
                    if title_name:
                        atag = title_name.find("a")
                        title = atag.text # type: ignore
                    
                    # item-genre
                    genres = []
                    tgenres = item.select(".fdi-item > a")
                    if tgenres:
                        genres = [i.text for i in tgenres]
                    
                    # latest-chapter
                
            else:
                raise Exception("No results found")
        
        except Exception as e:
            logger.error(f"Errro searching for {query} in {MangaReader.domain}: {e}")
        
        return results