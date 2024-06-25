import logging

from drivers.base_client import BaseClient
from drivers.instagram import InstagramClient
from drivers.twitter import TwitterClient, TWITTER_CACHE_PATH
from utils.cache_service import CacheService


def mute_instagrapi_logger() -> None:
    logging.basicConfig(level=logging.ERROR)


def get_social_media_client() -> BaseClient:
    available_options = ['1', '2']
    selection = input(f'Select a social media (enter number):\n1) Instagram\n2) Twitter\n\n> ')
    if selection not in available_options:
        print(f"Invalid option. Available options are: {', '.join(available_options)}\n")
        get_social_media_client()

    if selection == '1':
        return InstagramClient()
    elif selection == '2':
        return TwitterClient(cache_service=CacheService(filename=TWITTER_CACHE_PATH))


def main():
    mute_instagrapi_logger()
    client = get_social_media_client()

    if client:
        client.block_users()


if __name__ == "__main__":
    main()
