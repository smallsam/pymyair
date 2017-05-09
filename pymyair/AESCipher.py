from Crypto.Cipher import AES
from Crypto import Random
import binascii, base64

# No longer required as Advantage Air seem to have removed AES encryption
# from their app's communication


class AESCipher:
    def __init__( self, key ):
        self.key = key
        self.bs = 16
        # for myair AES, initialisation vector is set statically to a nul string
        # and is not contained within ciphertext


    def encrypt( self, raw ):
        """
        Returns base64 encoded and MyAir AES encrypted string
        """
        iv =  bytes(16)
        cipher = AES.new(self.key, AES.MODE_CBC, iv )
        padded = self._pad(raw.encode('utf-8'))

        enc = cipher.encrypt(padded)
        # TODO fix for trailing '-'
        encoded = base64.urlsafe_b64encode(enc)
        return encoded.decode('utf-8')+'-'

    def decrypt( self, ciphertext ):
        """
        Returns plaintext from MyAir base64 and AES encrypted string
        """
        iv =  bytes(16)
        cipher = AES.new(self.key, AES.MODE_CBC, iv )
        if ciphertext[-1] == '-':
            decode = base64.urlsafe_b64decode(ciphertext[:-1])
            urlsafe = 1
        else:
            decode = base64.b64decode(ciphertext[:-1])
            urlsafe = 0

        print(decode)

        final = AESCipher.unpad(cipher.decrypt(decode)).decode('utf-8')
        print(str(len(final))+":"+final)
        if urlsafe == 0:
            plaintext = final
        else:
            plaintext = final[3:]
        return plaintext


    @staticmethod
    def str_to_bytes(data):
        u_type = type(b''.decode('utf8'))
        if isinstance(data, u_type):
            return data.encode('utf8')
        return data

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * AESCipher.str_to_bytes(chr(self.bs - len(s) % self.bs))

    @staticmethod
    def unpad(s):
        return s[:-ord(s[len(s)-1:])]

def swap(s, i, j):
    return ''.join((s[:i], s[j], s[i+1:j], s[i], s[j+1:]))
    
