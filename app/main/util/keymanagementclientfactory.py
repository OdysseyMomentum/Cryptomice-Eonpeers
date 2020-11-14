import os.path

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.exceptions import InvalidSignature 

"""
TODO: This class will handle the connection to KMIP-compliant key management server

at the moment the chosen reference is: https://pykmip.readthedocs.io/en/latest/index.html

TODO: once the functions from pykmip are clear, define the abastract methods
"""
#from kmip.pie import objects
#from kmip.pie import client
#from kmip import enums

class KeyManagementClientFactory:
    def __init__(self):
        self._builders = {}

    def register_builder(self, key, builder):
        self._builders[key] = builder

    def create(self, key, **kwargs):
        builder = self._builders.get(key)
        if not builder:
            # return default
            builder = DevKeyManagementClientBuilder(**kwargs)
        return builder(**kwargs)


class DevKeyManagementClientBuilder:
    def __init__(self, **_ignored):
        #TODO: **ignored could be the path where to look for and create the key file
        self._instance = None

    def __call__(self, **ignored):
        if not self._instance:
            self._instance = DevKeyManagementClient()
        return self._instance



class DevKeyManagementClient:
    #basic KM tool with a local private key saved in the __file__ folder
    #for developing, testing, sandbox usage only
    _type = 'DEV'
    _priv_key = None
    def __init__(self):
        try:
            self._priv_key = self._get_key();
        except OSError as e:
            self._priv_key = self._generate_key()
        except Exception as e:
            print(e)
            raise Exception('Something wrong with Key Management Init')

    def _get_key(self, *args, **kwargs):
        """
        Get the key from the default path 

        the default path for now is the same folder as the __file__,
        if the .pem is not there, OSError is raised so that
        the caller can act accordingly. Notice that DEVClient uses EC.

        Params:
        -------

        Returns:
        --------
        EllipticCurvePrivateKey
            as for the cryptography library

        Raises:
        -------
        OSError
            When the file is not there
        ValueError, TypeError, UnsupportedAlgorithm
            When there is something wrong in the file

        """
        filename = os.path.join(os.path.dirname(__file__), 'privkey.pem')
        with open(filename, 'rb') as pem_in:
            pemlines = pem_in.read()
        priv_key = load_pem_private_key(pemlines, None, default_backend())
        pub_key = priv_key.public_key()
        serialized_pub_key = pub_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return priv_key


    def _generate_key(self, *args, **kwargs):
        """
        Generate a new key 

        the default path for now is the same folder as the __file__,
        a new file will be saved there and it will be a PEM
        representation of an EC private key

        Params:
        -------

        Returns:
        --------
        EllipticCurvePrivateKey
            as for the cryptography library

        Raises:
        -------
        OSError
            When there are problems in writing the file

        """
        priv_key = ec.generate_private_key(ec.SECP384R1(), default_backend())
        filename = os.path.join(os.path.dirname(__file__), 'privkey.pem')
        pem = priv_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        )
        with open(filename, 'wb') as pem_out:
            pem_out.write(pem)
        return priv_key

    def get_serialized_pub_key(self):
        """
        Get the serialised public key with PEM encoding of this eonpass node

        Params
        ------

        Returns
        -------
        bytes
            the serialised data with the PEM encoding

        Raises
        ------

        """
        priv_key = self._priv_key
        pub_key = priv_key.public_key()
        serialized_key = pub_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return serialized_key

    def sign_bytes_message(self, message):
        """
        sign a message with the local liquid node

        get a local address, use its embedded.confidential_key as private key
        and return the signed message and its serialized public_key
        
        Parameters
        ----------
        message: bytes
            the message to be signed by the node

        Returns
        --------
        dict
            {signed, serialized_public}, a JSON containind the
            signed messaged and its respective serialized public key
            in bytes


        Raises
        ------
        Exception
            when message is not in bytes

        """

        priv_key = self._priv_key
        pub_key = priv_key.public_key()
        serialized_key = pub_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        signed = priv_key.sign(message, ec.ECDSA(hashes.SHA256()))
        return {'signed': signed, 'serialized_public': serialized_key}


    def verify_signed_message(self, signed, message, serialized_public):
        """
        check if a message and a signature are matching given the pub key 

        note that the signature may be sent over by another node, 
        therefore we also need to know the public_key

        Parameters
        ----------
        signed: bytes
            the signed version

        message: str or bytes
            the original message that was signed

        serialized_public: str (utf-8 decoded) or bytes
            the public key in PEM encoding

        Returns
        --------
        bool
            True if the signed message check out, False otherwise.
            Note that anything going wrong is catched and 
            the method just returns False
        """
        try:
            print("inside factory")
            if(isinstance(serialized_public, str)):
                serialized_public = serialized_public.encode()
            loaded_public_key = serialization.load_pem_public_key(
                serialized_public,
                backend=default_backend()
            )
            if(isinstance(message, str)):
                message = message.encode()
                
            # this raises exception if the signature is not valid
            loaded_public_key.verify(
                signed, message, ec.ECDSA(hashes.SHA256())) #bytes -> str: decode; str->bytes: encode
            return True
        except ValueError as ve:
            print("value error", ve)
            return False
        except InvalidSignature  as invalid:
            print("invalid", invalid)
            return False
        except Exception as e:
            print("general exc", e)
            return False

