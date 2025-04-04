# core/services/keychain_manager.py

from typing import Optional

import keyring
from keyring.errors import KeyringError, PasswordDeleteError


class SudoKeychainManager:
    """
    Encapsulates storing and retrieving the sudo password in macOS Keychain using the `keyring` library.
    This class provides methods to securely save, retrieve, and delete the sudo password in the macOS Keychain.
    """

    def __init__(
        self, service_name: str = "StardustVPNApp", account_name: str = "sudo_password"
    ):
        """
        Initializes the SudoKeychainManager with the specified service and account names.

        :param service_name: The 'service' label under which the password is stored in the Keychain.
                             Defaults to "StardustVPNApp".
        :param account_name: The 'account' (or 'username') label under which the password is stored.
                             Defaults to "sudo_password".
        """
        self._service_name = service_name
        self._account_name = account_name

    def store_sudo_password(self, password: str) -> None:
        """
        Saves the given password in the macOS Keychain under the specified service and account names.
        If the user hasn't previously allowed access, a Keychain popup may appear.

        :param password: The sudo password to be securely stored in the Keychain.
        :raises keyring.errors.KeyringError: If there is an issue storing the password.
        """
        try:
            keyring.set_password(self._service_name, self._account_name, password)
        except KeyringError as exc:
            raise ValueError(f"Failed to store password: {exc}") from exc

    def get_sudo_password(self) -> Optional[str]:
        """
        Retrieves the sudo password from the macOS Keychain.
        If the password is not found or access is denied, an exception is raised.

        :return: The stored sudo password as a string, if found.
        :raises ValueError: If the password is not found or access is denied.
        """
        try:
            result = keyring.get_password(self._service_name, self._account_name)

            if not result:
                raise ValueError("Password not found or access denied.")

            return result
        except KeyringError as exc:
            raise ValueError(f"Failed to retrieve password: {exc}") from exc

    def clear_sudo_password(self) -> None:
        """
        Removes the stored sudo password entry from the macOS Keychain, if it exists.

        :raises keyring.errors.PasswordDeleteError: If there is an issue deleting the password.
        """
        try:
            keyring.delete_password(self._service_name, self._account_name)
        except PasswordDeleteError:
            pass
