from typing import Optional

from instagrapi import Client
from instagrapi.exceptions import UserNotFound

from drivers.base_client import BaseClient


class InstagramClient(BaseClient):
    def __init__(self):
        super().__init__()
        self.client = self.start_client()
        self.usernames_filename = "instagram_usernames.txt"

    @staticmethod
    def start_client() -> Client:
        print('Logging in to Instagram...')
        username = input(f'Enter your Instagram username: ')
        password = input(f'Enter your Instagram password: ')

        client = Client()
        client.login(username, password)
        print('Successfully logged in to Instagram.')
        return client

    def get_usernames_from_file(self) -> list[str]:
        try:
            with open(self.usernames_filename, "r") as file:
                print(f'Reading usernames from file: {self.usernames_filename}')
                return file.read().splitlines()
        except FileNotFoundError:
            raise Exception(f"Error: {self.usernames_filename} file not found.")

    def get_user_id_from_username(self, username: str) -> Optional[str]:
        try:
            return self.client.user_info_by_username_v1(username).dict()['pk']
        except UserNotFound:
            print(f'User {username} has already been blocked or does not exist.')
            return

    def block_users(self) -> None:
        usernames = self.get_usernames_from_file()
        print("Blocking users...")
        for username in usernames:
            user_id = self.get_user_id_from_username(username)
            if user_id:
                self.client.user_block(user_id)
                print(f"User {username} with id {user_id} blocked successfully.")
        print("Blocking complete.")
