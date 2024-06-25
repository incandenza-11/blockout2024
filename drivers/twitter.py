import os
from typing import Optional

from twitter.account import Account
from twitter.scraper import Scraper

from drivers import PROJECT_ROOT_PATH
from drivers.base_client import BaseClient
from utils.cache_service import CacheService

TWITTER_CACHE_PATH = f'{PROJECT_ROOT_PATH}/resources/cache/twitter/cached_users.json'


class TwitterClient(BaseClient):
    def __init__(self, cache_service: CacheService):
        super().__init__(cache_service=cache_service)
        self.usernames_filename = f'{PROJECT_ROOT_PATH}/resources/usernames/twitter.txt'
        self.username: Optional[str] = None
        self.cookies_path = '{}/resources/cache/twitter/{}-cookies.json'.format(PROJECT_ROOT_PATH, '{username}')
        self.client, self.scraper = self.start_client()

    @staticmethod
    def _verify_user_has_active_session(cookies_path: str, username: str) -> bool:
        if os.path.exists(cookies_path):
            print(f'Found an active session for user {username} on path {cookies_path}. Logging in...')
            return True

        with open(cookies_path, 'w') as file:
            file.write("""{"ct0": "", "auth_token": ""}""")

        message = (f"Cookies are needed to log in to your Twitter account. Fill in the two cookies values on file "
                   f"{cookies_path} and try again.\nYou can find these values logging into Twitter from your browser "
                   f"-> Inspector -> Application -> Cookies.\nCopy the 'ct0' and 'auth_token' values and paste "
                   f"them into its corresponding key within cookies file and run the script again.")
        print(message)
        raise Exception(message)

    def _set_credentials(self):
        self.username = input('Enter your Twitter username: ')
        self.cookies_path = self.cookies_path.format(username=self.username)
        self._verify_user_has_active_session(cookies_path=self.cookies_path, username=self.username)

    def start_client(self) -> tuple[Account, Scraper]:
        self._set_credentials()
        account = Account(cookies=self.cookies_path)
        scraper = Scraper(cookies=self.cookies_path)
        print(f'Successfully logged in to Twitter')
        return account, scraper

    def _get_non_cached_users(self, usernames: list[str]) -> list[str]:
        return [x for x in usernames if self.cache_service.get(x) is None]

    def _get_cached_user_ids(self, usernames: list[str]) -> list[int]:
        return [self.cache_service.get(x) for x in usernames if self.cache_service.get(x) is not None]

    def _get_user_ids_by_usernames(self, usernames: list[str], chunk_size: int = 20) -> dict[str, int]:
        print(f'Retrieving information of {len(usernames)} Twitter users...')
        chunked_usernames_list = [usernames[i:i + chunk_size] for i in range(0, len(usernames), chunk_size)]
        user_ids_to_block = {}

        try:
            for i, usernames_chunk in enumerate(chunked_usernames_list):
                print(f'Fetching info of {len(usernames_chunk)} users ({i+1}/{len(chunked_usernames_list)})')

                # Process cached users
                users_data = self.scraper.users_by_ids(self._get_cached_user_ids(usernames_chunk))
                if users_data:
                    for user_data in users_data[0]['data']['users']:
                        if not user_data:
                            continue
                        # If user is not already blocked
                        if not user_data['result']['legacy'].get('blocking', False) is True:
                            username, user_id = user_data['result']['legacy']['screen_name'], int(user_data['result']['rest_id'])
                            user_ids_to_block[username] = user_id

                # Process non-cached users
                for user_data in self.scraper.users(self._get_non_cached_users(usernames_chunk)):
                    try:
                        if not user_data:
                            continue
                        result = user_data['data']['user']['result']
                        username, user_id = result['legacy']['screen_name'], int(result['rest_id'])
                        self.cache_service.set(key=username, value=user_id)
                        if not result['legacy'].get('blocking', False) is True:  # If user is not already blocked
                            user_ids_to_block[username] = user_id
                    except Exception as e:
                        print(f'Exception saving user id: {e}')
                        continue
        except Exception as e:
            print(f'Error while retrieving user data: {e}')

        print(f'Found {len(user_ids_to_block)}/{len(usernames)} users ready to be blocked.') if user_ids_to_block \
            else print("Couldn't find any user to block.")

        return user_ids_to_block

    def block_users(self) -> None:
        usernames = self.get_usernames_from_file(file_path=self.usernames_filename)
        users_to_block = self._get_user_ids_by_usernames(usernames=usernames)

        if users_to_block:
            print(f'Blocking {len(users_to_block)} users...')
            for username, user_id in users_to_block.items():
                self.client.block(user_id=user_id)
                print(f'User {username} blocked successfully')

            print("Blocking complete.")
