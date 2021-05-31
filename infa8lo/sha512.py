import hashlib
import base64

# hashedPassword = Hash("password_to_hash")
# print(hashedPassword)
# if hashedPassword = hashedPassword1

class Hash:
    def __init__(self, password):
        self.sha512 = hashlib.sha512(password.encode()).digest()
        self.base64 = base64.b64encode(self.sha512)
        self.toStore = f'{{sha512}}{str(self.base64)[2:-1]}'

    def __str__(self):
        return f'{self.toStore}'

    def __eq__(self, other):
        return (isinstance(other, self.__class__)
            and self.toStore == other.toStore)
