from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from typing import *
import secrets
import hashlib
import hmac
import os

HASH_VALUES : List[str] = [
    "0xd9596f25",
    "0xd6ce429b",
    "0xd897d13b",
    "0xf9b80387",
    "0xb344752f",
    "0x90156176",
    "0x79a7c49c",
    "0x440365a7",
]

K : List[str]= [
    "0x177f2c45", "0xaaced748", "0x9d4159ea", "0xadcbd874", 
    "0xd5b7dcbe", "0x633b1ec7", "0xd1f76f3e", "0x669c8877", 
    "0x2781a573", "0xa5cbe1a5", "0x973b978a", "0x1019f219", 
    "0xe0b369bc", "0x118aeb2f", "0xf020ed3f", "0xfcf25075", 
    "0x917daa56", "0xd23ae6f5", "0x4fdfd7a6", "0x1a4936fe", 
    "0x499b8dbe", "0x0494caa2", "0xfe1c8a57", "0x9568a7c7", 
    "0xbdf4f023", "0x8a163441", "0xf8649355", "0x6ee82ea0", 
    "0xd23e9bba", "0xfc18aaa2", "0x458bcdce", "0x1746ef78", 
    "0xe2c56801", "0xee3309e8", "0x479bcafa", "0xed1e5952", 
    "0xb1c5a509", "0x8aa8104d", "0xcfcce872", "0x067bc9b1", 
    "0xa73081f8", "0x2aa97233", "0xb2c191d0", "0xe85ce99d", 
    "0x6874237e", "0xb8570681", "0xddd77e5d", "0x19149e04", 
    "0xe7be85d5", "0xbedab1b7", "0x718db8b1", "0x6de28255", 
    "0x3f84fbe2", "0x825c298c", "0x0eae69bb", "0x3696a968", 
    "0x8314b735", "0x431d32c0", "0x9786fd39", "0x0e069d62", 
    "0xeb532d85", "0x1d78c430", "0xcfb1e41b", "0xc8fe13f1"
]

def generateRandomHex(length : int):
    return "0x" + secrets.token_hex(length // 2)

def stringToBits(message : str) -> List[int]:
    charcodes : List[int] = [ord(c) for c in message]
    bytes_array : List[str] = []
    
    for char in charcodes:
        bytes_array.append(bin(char)[2:].zfill(8))
        
    bits : List[int] = []
    for byte in bytes_array:
        for bit in byte:
            bits.append(int(bit))
    return bits

def binaryToHexadecimal(bit_array : List[int]) -> str:
    value = "".join([str(x) for x in bit_array])
    binaries : List[str] = []
    for d in range(0, len(value), 4):
        binaries.append("0b" + value[d:d+4])
    hexadceimal_value : str = ""
    for b in binaries:
        hexadceimal_value += hex(int(b ,2))[2:]
    return hexadceimal_value

def fillZeros(bit_array : List[int], length : Optional[int] = 8 , endian : Optional[str] = "LE") -> List[int]:
    if endian == "LE":
        return bit_array + (length-len(bit_array))*[0]
    elif endian == "BE":
        return (length-len(bit_array))*[0] + bit_array
    else:
        raise Exception("Enter either LE or BE")

def createChunks(bit_array : List[int], chunk_size : Optional[int] = 8) -> List[List[int]]:
    chunks : List[List[int]]= []
    for i in range(0, len(bit_array), chunk_size):
        chunks.append(bit_array[i:i+chunk_size])
    return chunks

def initializer(values : List[str]) -> List[List[int]]:
    binaries : List[str]= [bin(int(v, 16))[2:] for v in values]
    words : List[List[int]] = []
    for binary in binaries:
        word : List[int] = []
        for b in binary:
            word.append(int(b))
        words.append(fillZeros(word, 32, 'BE'))
    return words

def processText(text : str) -> List[List[int]]:   
    bits : List[int] = stringToBits(text)
    length : int = len(bits)
    text_len = [int(b) for b in bin(length)[2:].zfill(64)]
    if length < 448:
        bits.append(1)
        bits = fillZeros(bits, 448, 'LE')
        bits += text_len
        return [bits]
    elif 448 <= length <= 512:
        bits.append(1)
        bits = fillZeros(bits, 1024, 'LE')
        bits[-64:] = message_len
        return createChunks(bits, 512)
    else:
        bits.append(1)
        while (len(bits)+64) % 512 != 0:
            bits.append(0)    
        bits += text_len
        return createChunks(bits, 512)

def isTrue(x:int) -> bool: 
    return x == 1

def if_(i, y, z): 
    return y if isTrue(i) else z

def and_(i, j): 
    return if_(i, j, 0)

def AND(i, j): 
    return [and_(ia, ja) for ia, ja in zip(i,j)] 

def not_(i): 
    return if_(i, 0, 1)
def NOT(i): 
    return [not_(x) for x in i]

def xor(i, j): 
    return if_(i, not_(j), j)
def XOR(i, j): 
    return [xor(ia, ja) for ia, ja in zip(i, j)]

def xorxor(i, j, l): 
    return xor(i, xor(j, l))

def XORXOR(i, j, l): 
    return [xorxor(ia, ja, la) for ia, ja, la, in zip(i, j, l)]

def maj(i,j,k): 
    return max([i,j,], key=[i,j,k].count)

def rotr(x, n): 
    return x[-n:] + x[:-n]

def shr(x, n): 
    return n * [0] + x[:-n]

def add(i, j):
    length = len(i)
    sums = list(range(length))
    c = 0
    for x in range(length-1,-1,-1):
        sums[x] = xorxor(i[x], j[x], c)
        c = maj(i[x], j[x], c)
    return sums

def sha256(text : str) -> str: 
    k = initializer(K)
    h0, h1, h2, h3, h4, h5, h6, h7 = initializer(HASH_VALUES)
    chunks = processText(text)
    for chunk in chunks:
        w = createChunks(chunk, 32)
        for _ in range(48):
            w.append(32 * [0])
        for i in range(16, 64):
            s0 = XORXOR(rotr(w[i-15], 7), rotr(w[i-15], 18), shr(w[i-15], 3) ) 
            s1 = XORXOR(rotr(w[i-2], 17), rotr(w[i-2], 19), shr(w[i-2], 10))
            w[i] = add(add(add(w[i-16], s0), w[i-7]), s1)
        a = h0
        b = h1
        c = h2
        d = h3
        e = h4
        f = h5
        g = h6
        h = h7
        for j in range(64):
            S1 = XORXOR(rotr(e, 6), rotr(e, 11), rotr(e, 25) )
            ch = XOR(AND(e, f), AND(NOT(e), g))
            temp1 = add(add(add(add(h, S1), ch), k[j]), w[j])
            S0 = XORXOR(rotr(a, 2), rotr(a, 13), rotr(a, 22))
            m = XORXOR(AND(a, b), AND(a, c), AND(b, c))
            temp2 = add(S0, m)
            h = g
            g = f
            f = e
            e = add(d, temp1)
            d = c
            c = b
            b = a
            a = add(temp1, temp2)
        h0 = add(h0, a)
        h1 = add(h1, b)
        h2 = add(h2, c)
        h3 = add(h3, d)
        h4 = add(h4, e)
        h5 = add(h5, f)
        h6 = add(h6, g)
        h7 = add(h7, h)
    digest = ''
    for val in [h0, h1, h2, h3, h4, h5, h6, h7]:
        digest += binaryToHexadecimal(val)
    return digest

def sign(message_hash, private_key):
    signature = private_key.sign(
        message_hash,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return signature

def verify(signature, message_hash, public_key):
    try:
        public_key.verify(
            signature,
            message_hash,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except Exception as e:
        print("Verification failed:", e)
        return False


def generateKeys():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()

    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    return private_key_pem, public_key_pem


def loadPrivateKey(private_key_pem):
    return serialization.load_pem_private_key(
        private_key_pem,
        password=None,
        backend=default_backend()
    )

def loadPublicKey(public_key_pem):
    return serialization.load_pem_public_key(
        public_key_pem,
        backend=default_backend()
    )

if __name__ == '__main__':
    private_key_pem, public_key_pem = generateKeys()
    private_key = loadPrivateKey(private_key_pem)
    public_key = loadPublicKey(public_key_pem)

    # Data to be signed
    data = "Your data to be signed"
    hash_data = sha256(data).encode()

    # Sign the data
    signature = sign(hash_data, private_key)

    # Simulate tampering with the signature
    tampered_signature = bytearray(signature)
    tampered_signature[0] ^= 1  # Flip the first bit of the signature

    # Verify the tampered signature
    is_valid = verify(tampered_signature, hash_data, public_key)

    if is_valid:
        print("Signature is valid.")
    else:
        print("Signature is not valid.")


# if __name__ == '__main__':
#     # Generate RSA key pair
#     private_key_pem, public_key_pem = generateKeys()
#     private_key = loadPrivateKey(private_key_pem)
#     public_key = loadPublicKey(public_key_pem)

#     # Data to be signed
#     data = "Your data to be signed"
#     hash_data = sha256(data).encode()

#     # Sign the data
#     signature = sign(hash_data, private_key)

#     # Verify the signature
#     is_valid = verify(signature, hash_data, public_key)

#     if is_valid:
#         print("Signature is valid.")
#     else:
#         print("Signature is not valid.")


# if __name__ == '__main__':
#     # verdict = 'y'
#     # while verdict == 'y':
#     #     input_message = input('Type or copy your message here: ')
#     #     print('Your message: ', input_message)
#     #     print('Hash: ', sha256(input_message))
#     #     verdict = input('Do you want to tryte another text? (y/n): ').lower()  
#     # Example usage
#     private_key, public_key = generateKeys()
#     print("Private Key:")
#     print(private_key.decode())
#     print("\nPublic Key:")
#     print(public_key.decode())
#     # Data to be signed
#     data = "Your data to be signed"
#     hash_data = sha256(data)

#     # Sign the data
#     # Sign the data
#     signature = sign(hash_data.encode(), private_key)  # Ensure hash_data is encoded as bytes


#     # Verify the signature
#     is_valid = verify(signature, hash_data.encode(), public_key)  # Ensure hash_data is encoded as bytes


#     if is_valid:
#         print("Signature is valid.")
#     else:
#         print("Signature is not valid.")