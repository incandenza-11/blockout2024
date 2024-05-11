import logging

from drivers.base_client import BaseClient
from drivers.instagram import InstagramClient


def mute_instagrapi_logger() -> None:
    logging.basicConfig(level=logging.ERROR)


def get_social_media_client() -> BaseClient:
    available_options = ['1', '2']
    selection = input(f'Select a social media (enter number):\n1) Instagram\n2) TikTok\n\n> ')
    if selection not in available_options:
        print(f"Invalid option. Available options are: {', '.join([x for x in available_options])}")
        get_social_media_client()

    if selection == '1':
        return InstagramClient()
    else:
        print('TikTok is still in progress.')
        return get_social_media_client()


def main():
    mute_instagrapi_logger()
    client = get_social_media_client()

    if client:
        client.block_users()


if __name__ == "__main__":
    main()
