import random
import giphy_client
from giphy_client.rest import ApiException


class MediaManager:
    """
    Serves as the main media access layer
    """

    def __init__(self, giphy_key:str=""):
        self.giphy_key = giphy_key
        self.giphy_api = giphy_client.DefaultApi()

    def get_gif(self, keyword, limit=10, rating='g', lang = 'en') -> str:
        """
        Returns a GIF url based on the inputted keyword.
        
        @param keyword: Search query term or prhase.
        @param limit: The maximum number of records to return.
        @param rating: The message's user name
        @param lang: Specify default country for regional content; use a 2-letter ISO 639-1 country code.
        @return gif_url: The message's channel id
        """
        gif_url = ""
        try: 
            api_response = self.giphy_api.gifs_search_get(self.giphy_key, keyword,
                                                          limit=limit, rating=rating,
                                                          lang=lang, fmt='json')
        except ApiException as e:
            raise ValueError("Exception when calling DefaultApi->gifs_search_get: %s\n" % e)

        links = []
        for data in api_response.data:
            links.append(data.bitly_gif_url)

        gif_url = random.choice(links)
        return gif_url