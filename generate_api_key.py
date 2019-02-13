import uuid
import hashlib


apikey = uuid.uuid4()

print("Provide the key below to the client")
print("================================")
print(apikey.hex)
print("================================")

print("\nStore the hashed key below in the APIKEYS environment variable")
# generate a hash for the key
hp = hashlib.sha256(apikey.hex.encode('ascii')).hexdigest()

print("================================================================")
print (hp)
print("================================================================")

