
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization, hmac
from cryptography.hazmat.primitives.asymmetric import ec

from flask import current_app

class Singleton(object):
    _instance = None  # Keep instance reference

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance


class HashUtils(Singleton):

    def __init__(self):
        #perfrom init if needed
        return

    def digest(self, message):
        """
        digest a message: perform SHA256

        first check if the message is a string, if not .encode() it,
        then perform the digest operation

        Parameters
        ----------
        message: str or bytes
            the message to be hashed

        Returns
        --------
        bytes
            the hashed message in bytes

        Raises
        ------
        Exception
            if the input message is not a string or bytes raise a
            general exception

        """
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        if(isinstance(message, str)):
            digest.update(message.encode())
        elif(isinstance(message, bytes)):
            digest.update(message)
        else:
            raise Exception('Corrupt message type')
        bytes_digest = digest.finalize()
        return bytes_digest

    def hmac(self, message, key):
        """
        compute the hmac of the given message and key

        the inbound key is a location_key, therefore we hash it to obtain a 256bit key
        which is the suggeste length for hmac keys (same length as the final digest)

        Parameters
        ----------
        message: str or bytes
            the message to be hashed
        key: str or bytes
            the key for the hmac

        Returns
        --------
        bytes
            the hashed message in bytes

        Raises
        ------
        Exception
            if the inputs are not a string or bytes raise a
            general exception
        """
        correct_length_bit_key = self.digest(key)
        message = message.encode() if isinstance(message, str) else message
        h = hmac.HMAC(correct_length_bit_key, hashes.SHA256(), backend=default_backend())
        h.update(message)
        return h.finalize()