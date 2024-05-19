from typing import Optional

from instagrapi import Client
from instagrapi.exceptions import UserNotFound, ChallengeRequired, TwoFactorRequired, LoginRequired

from drivers.base_client import BaseClient


class InstagramClient(BaseClient):
    def __init__(self):
        super().__init__()
        self.client = self.start_client()
        if self.client is None:
            raise Exception("Failed to initialize Instagram client.")
        self.usernames_filename = "resources/usernames/instagram.txt"

    @staticmethod
    def start_client() -> Optional[Client]:
        print('Logging in to Instagram...')
        username = input('Enter your Instagram username: ')
        password = input('Enter your Instagram password: ')

        client = Client()

        try:
            client.login(username, password)
        except TwoFactorRequired:
            print('Two-factor authentication required.')
            two_factor_code = input('Enter the 2FA code: ')
            try:
                client.login(username, password, verification_code=two_factor_code)
            except Exception as e2:
                print(f'Two-factor login error: {e2}')
                return None
        except ChallengeRequired:
            print('Challenge required. Please approve the login on your Instagram app or enter the code sent to your email/phone.')
            try:
                client.challenge_resolve(client.last_json)
            except Exception as e2:
                print(f'Challenge error: {e2}')
                return None
        except Exception as e:
            print(f'Login error: {e}')
            return None

        client.delay_range = [1, 4]
        print('Successfully logged in to Instagram.')
        return client

    def ensure_logged_in(self):
        try:
            self.client.get_timeline_feed()  # Checking if session is valid
        except LoginRequired:
            print('Session expired or invalid. Logging in again...')
            self.client = self.start_client()
            if self.client is None:
                raise Exception("Failed to reinitialize Instagram client.")

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
        usernames_to_block = set(self.get_usernames_from_file())

        print("Blocking users...")
        for username in usernames_to_block:
            user_id = self.get_user_id_from_username(username)
            if user_id:
                self.client.user_block(user_id)
                print(f"User {username} with id {user_id} blocked successfully.")
            else:
                print(f"User {username} is already blocked or does not exist.")
        print("Blocking complete.")


# Entry point for the script
def main():
    client = InstagramClient()
    client.block_users()


if __name__ == "__main__":
    main()
