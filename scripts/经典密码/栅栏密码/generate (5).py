flag = open('./flag').read()
substitution = ['h', 'k', 'S', 'A', 'D', 'm', 'G', 'O', 'o', 'L', 'E', 'b', 'l', 'M', 'K', 't', 'X', 'f', 'Q', 'j', 'z', 'U','g', 'c', 'v', 'u',
       'F', 'C', 'e', 'n', 'B', 'J', 'P', 'I', 'V', 'N', 'Z', 'i', 'q', 'a', 'W', 'H', 'p', 'R', 'w', 'T', 'r', 'Y', 'd', 'x', 's', 'y']

assert(len(flag) % 3 == 0)

cipher1 = ''
for ch in flag:
    if 'A' <= ch <= 'Z':
        idx = ord(ch) - ord('A')
        cipher1 += substitution[idx]
    elif 'a' <= ch <= 'z':
        idx = ord(ch) - ord('a') + 26
        cipher1 += substitution[idx]
    else:
        cipher1 += ch

cipher2 = ''
for j in range(3):
    for i in range(len(flag)//3):
        cipher2 += cipher1[i*3+j]

print(cipher2.encode().hex())