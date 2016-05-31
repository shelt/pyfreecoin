alphabet = '123456789abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ'
base_count = len(alphabet)
		
def b58_encode(num):
	""" Returns num in a base58-encoded string """
	encode = ''
	
	if (num < 0):
		return ''
	
	while (num >= base_count):	
		mod = num % base_count
		encode = alphabet[mod] + encode
		num = int(num / base_count)

	if (num):
		encode = alphabet[num] + encode

	return encode

def b58_decode(s):
	""" Decodes the base58-encoded string s into an integer """
	decoded = 0
	multi = 1
	s = s[::-1]
	for char in s:
		decoded += multi * alphabet.index(char)
		multi = multi * base_count
		
	return decoded
