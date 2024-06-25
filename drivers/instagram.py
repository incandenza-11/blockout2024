import os.path
from getpass import getpass
from pathlib import Path
from typing import Optional

from instagrapi import Client
from instagrapi.exceptions import (
    UserNotFound,
    ChallengeRequired,
    TwoFactorRequired,
    LoginRequired,
    PleaseWaitFewMinutes,
)

from drivers import PROJECT_ROOT_PATH
from drivers.base_client import BaseClient


class InstagramClient(BaseClient):
    def __init__(self):
        super().__init__()
        self.usernames_filename = f"{PROJECT_ROOT_PATH}/resources/usernames/instagram.txt"
        self.cache_dir = f"{PROJECT_ROOT_PATH}/resources/cache/instagram"
        self.blocked_users_filename = "{}/{}-blocked_users.txt".format(self.cache_dir, "{username}")
        self.session_path_by_username = "{}/{}-session.json".format(self.cache_dir, "{username}")
        self.username: Optional[str] = None
        self.client = self.start_client()

    @staticmethod
    def _append_to_cache(filename: str, content: str) -> None:
        with open(filename, "a", encoding="utf-8") as file:
            file.write(f"{content}\n")

    def _ensure_logged_in(self) -> None:
        try:
            self.client.get_timeline_feed()  # Checking if session is valid
        except LoginRequired:
            print("Session expired or invalid. Logging in again...")
            self.client = self.start_client()
        except PleaseWaitFewMinutes:
            print(
                "\nPlease wait a few minutes to try again... If it does not help, "
                "run `make ig/clear-session` to clear instagram session\n"
            )

    def _user_has_session(self, username: str) -> bool:
        return os.path.exists(self.session_path_by_username.format(username=username))

    def log_in(
        self,
        client: Client,
        username: str,
        password: str,
        verification_code: Optional[str] = None,
    ) -> None:
        client.login(
            username=username,
            password=password,
            verification_code=verification_code if verification_code else "",
        )
        if not self._user_has_session(username=username):
            client.dump_settings(Path(self.session_path_by_username.format(username=username)))

    def start_client(self) -> Optional[Client]:
        print("Logging in to Instagram...")
        self.username = input("Enter your Instagram username: ")
        password = getpass("Enter your Instagram password: ")
        client = Client()

        if self._user_has_session(self.username):
            session_filename = self.session_path_by_username.format(username=self.username)
            client.load_settings(Path(session_filename))

        try:
            self.log_in(client=client, username=self.username, password=password)

        except TwoFactorRequired:
            print("Two-factor authentication required.")
            two_factor_code = input("Enter the 2FA code: ")
            try:
                self.log_in(
                    client=client,
                    username=self.username,
                    password=password,
                    verification_code=two_factor_code,
                )
            except Exception as e2:
                raise Exception(f"Two-factor login error: {e2}") from e2
        except ChallengeRequired:
            print(
                "Challenge required. Please approve the login on your Instagram app "
                "or enter the code sent to your email/phone."
            )
            try:
                client.challenge_resolve(client.last_json)
            except Exception as e2:
                raise Exception(f"Challenge error: {e2}") from e2
        except Exception as e:
            raise Exception(f"Error initializing Instagram client: {e}") from e

        client.delay_range = [1, 4]
        print("Successfully logged in to Instagram.")
        return client

    def get_user_id_from_username(self, username: str) -> Optional[str]:
        try:
            self._ensure_logged_in()
            return self.client.user_info_by_username_v1(username).dict()["pk"]
        except UserNotFound:
            print(f"User {username} has already been blocked or does not exist.")
            return None

    def block_users(self) -> None:
        self._ensure_logged_in()
        usernames_to_block = self.get_usernames_from_file(file_path=self.usernames_filename)
        blocked_users_file = self.blocked_users_filename.format(username=self.username)
        blocked_usernames = []

        if os.path.exists(blocked_users_file):
            blocked_usernames.extend(self.get_usernames_from_file(file_path=blocked_users_file))
        else:
            # Create the cache file if it doesn't exist
            with open(blocked_users_file, "w", encoding="utf-8"):
                pass

        print("Blocking users...")
        for username in usernames_to_block:
            if username in blocked_usernames:
                print(f"User {username} is already blocked")
                continue

            user_id = self.get_user_id_from_username(username)
            if user_id:
                self.client.user_block(user_id)
                print(f"User {username} with id {user_id} blocked successfully.")
            self._append_to_cache(filename=blocked_users_file, content=username)

        print("Blocking complete.")


def main():
    client = InstagramClient()
    client.block_users()


if __name__ == "__main__":
    main()
