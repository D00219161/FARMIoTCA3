from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub

server_UUID = "df89d8b2-358e-11eb-adc1-0242ac120002"  # UUID Generated
cipherKey = "myCipherKey"  # Cipher Key
myChannel = "Homesafe"  # Channel Name

############################
pnconfig = PNConfiguration()

# Homesafe PubNub Connections - All members have access using these
pnconfig.subscribe_key = 'sub-c-12924b4c-2f48-11eb-9713-12bae088af96'
pnconfig.publish_key = 'pub-c-4c71c151-b075-498f-bfbc-c6f3221ed3b6'
pnconfig.secret_key = "sec-c-MTliZTg5YmItYjE3Zi00OGYxLTgwZDEtOTE5OGY5NDlmNWVk"
pnconfig.uuid = server_UUID
pnconfig.cipher_key = cipherKey
pubnub = PubNub(pnconfig)


def grant_access(auth_key, read, write):
    if read is True and write is True:
        grant_read_and_write_access(auth_key)
    elif read is True:
        grant_read_access(auth_key)
    elif write is True:
        grant_write_access(auth_key)
    else:
        revoke_access(auth_key)


def grant_read_and_write_access(auth_key):
    v = pubnub.grant() \
        .read(True) \
        .write(True) \
        .channels(myChannel) \
        .auth_keys(auth_key) \
        .ttl(6000) \
        .sync()
    print("------------------------------------")
    print("--- Granting Read & Write Access ---")
    for key, value in v.status.original_response.items():
        print(key, ":", value)
    print("------------------------------------")


def grant_read_access(auth_key):
    v = pubnub.grant() \
        .read(True) \
        .channels(myChannel) \
        .auth_keys(auth_key) \
        .ttl(6000) \
        .sync()
    print("------------------------------------")
    print("--- Granting Read Access ---")
    for key, value in v.status.original_response.items():
        print(key, ":", value)
    print("------------------------------------")


def grant_write_access(auth_key):
    v = pubnub.grant() \
        .write(True) \
        .channels(myChannel) \
        .auth_keys(auth_key) \
        .ttl(6000) \
        .sync()
    print("------------------------------------")
    print("--- Granting Write Access ---")
    for key, value in v.status.original_response.items():
        print(key, ":", value)
    print("------------------------------------")


def revoke_access(auth_key):
    v = pubnub.revoke() \
        .channels(myChannel) \
        .auth_keys(auth_key) \
        .sync()
    print("------------------------------------")
    print("--- Revoking Access ---")
    for key, value in v.status.original_response.items():
        print(key, ":", value)
    print("------------------------------------")
