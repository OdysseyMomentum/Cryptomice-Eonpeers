
from flask import current_app

from app.main.util.keymanagementclientfactory import KeyManagementClientFactory

class Singleton(object):
    _instance = None  # Keep instance reference

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance


class KeyManagementClient(Singleton):
    #on creation, get the enviornment type and call the factory accordingly
    _kmic = None

    def __init__(self):
        return

    def _get_kmic(self):
        if not self._kmic:
            factory = KeyManagementClientFactory();
            self._kmic = factory.create(current_app.config['KMI_TYPE'])
        return self._kmic

    def sign_message(self, message):
        """
        sign a message  with one of the keys avaialble on the node

        before doing the signature this methods checks if the message
        needs to be converted to bytes
        
        Parameters
        ----------
        message: str/bytes
            the message to be signed by the node, if str, it gets encoded first

        Returns
        --------
        dict
            {signed, serialized_public}, a JSON containind the
            signed messaged and its respective serialized public key 

        Raises
        ------
        Exception
            sign_bytes_message uses celery to retrieve keys from the node
            every time a response from celery if checked (_check_rpc_error)
            if an error was reported by the node, an Exception is raised
            with the error message as content

            if the message is not a string, not a bytes array,
            a general Exception is raised complaining about the message type
        """
        if isinstance(message, str):
            return self._get_kmic().sign_bytes_message(message.encode())
        elif isinstance(message, bytes):
            return self._get_kmic().sign_bytes_message(message)
        else:
            raise Exception('Corrupt message type')

    def verify_signed_message(self, signed, message, serialized_public):
        """
        check if a message and a signature are matching given the pub key 

        Parameters
        ----------
        signed: str
            the signed version

        message: str
            the original message that was signed

        serialized_public: str
            the public kley

        Returns
        --------
        bool
            True if the signed message check out, False otherwise.
            Note that anything going wrong is catched and 
            the method just returns False
        """
        return self._get_kmic().verify_signed_message(signed, message, serialized_public)

    def get_serialized_pub_key(self):
        """
        Get the serialised public key with PEM encoding of this eonpass node

        Params
        ------

        Returns
        -------
        str
            the serialised data with the PEM encoding

        Raises
        ------

        """
        return self._get_kmic().get_serialized_pub_key()


