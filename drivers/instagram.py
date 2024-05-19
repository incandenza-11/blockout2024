import os.path
from pathlib import Path
from typing import Optional

from instagrapi import Client
from instagrapi.exceptions import UserNotFound, ChallengeRequired, TwoFactorRequired, LoginRequired

from drivers import PROJECT_ROOT_PATH
from drivers.base_client import BaseClient


class InstagramClient(BaseClient):
    def __init__(self):
        super().__init__()
        self.usernames_filename = f'{PROJECT_ROOT_PATH}/resources/usernames/instagram.txt'
        self.cache_dir = f'{PROJECT_ROOT_PATH}/resources/cache/instagram'
        self.session_path_by_username = '{}/{}-session.json'.format(self.cache_dir, '{username}')
        self.client = self.start_client()

    def user_has_session(self, username: str) -> bool:
        return os.path.exists(self.session_path_by_username.format(username=username))

    def log_in(self, client: Client, username: str, password: str, verification_code: Optional[str] = None) -> None:
        client.login(username=username, password=password, verification_code=verification_code if verification_code else '')
        if not self.user_has_session(username=username):
            client.dump_settings(Path(self.session_path_by_username.format(username=username)))

    def start_client(self) -> Optional[Client]:
        print('Logging in to Instagram...')
        username = input('Enter your Instagram username: ')
        password = input('Enter your Instagram password: ')
        client = Client()

        if self.user_has_session(username):
            session_filename = self.session_path_by_username.format(username=username)
            client.load_settings(Path(session_filename))

        try:
            self.log_in(client=client, username=username, password=password)

        except TwoFactorRequired:
            print('Two-factor authentication required.')
            two_factor_code = input('Enter the 2FA code: ')
            try:
                self.log_in(client=client, username=username, password=password, verification_code=two_factor_code)
            except Exception as e2:
                raise Exception(f'Two-factor login error: {e2}')
        except ChallengeRequired:
            print('Challenge required. Please approve the login on your Instagram app or enter the code sent to your email/phone.')
            try:
                client.challenge_resolve(client.last_json)
            except Exception as e2:
                raise Exception(f'Challenge error: {e2}')
        except Exception as e:
            raise Exception(f'Error initializing Instagram client: {e}')

        client.delay_range = [1, 4]
        print('Successfully logged in to Instagram.')
        return client

    def ensure_logged_in(self) -> None:
        try:
            self.client.get_timeline_feed()  # Checking if session is valid
        except LoginRequired:
            print('Session expired or invalid. Logging in again...')
            self.client = self.start_client()

    def get_usernames_from_file(self) -> list[str]:
        try:
            with open(self.usernames_filename, "r") as file:
                print(f'Reading usernames from file: {self.usernames_filename}')
                return file.read().splitlines()
        except FileNotFoundError:
            raise Exception(f"Error: {self.usernames_filename} file not found.")

    def get_user_id_from_username(self, username: str) -> Optional[str]:
        try:
            self.ensure_logged_in()
            return self.client.user_info_by_username_v1(username).dict()['pk']
        except UserNotFound:
            print(f'User {username} has already been blocked or does not exist.')
            return None

    def block_users(self) -> None:
        self.ensure_logged_in()
        usernames_to_block = self.get_usernames_from_file()

        print("Blocking users...")
        for username in usernames_to_block:
            user_id = self.get_user_id_from_username(username)
            if user_id:
                self.client.user_block(user_id)
                print(f"User {username} with id {user_id} blocked successfully.")
        print("Blocking complete.")


def main():
    client = InstagramClient()
    client.block_users()


if __name__ == "__main__":
    main()
