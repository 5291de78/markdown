import base64
from fontTools.ttLib import TTFont
'''
with open("bs64.txt", "r") as file:
    b64 = file.read()
open("cipher.ttf", "wb").write(base64.b64decode(b64))
'''


font = TTFont("CIPHER3.ttf")
cmap = font.getBestCmap()

with open("cipher3.txt", "w") as file:
    file.write(str(cmap))
cipher = ""
for k in cmap.values():
    index = k.find("uni")
    if(index == -1):
        continue
    else:
        s = r"\u" + k[3+index:]
        cipher += s
with open("suspected_unicode.txt", "w") as file:
    file.write(str(cipher))
from fontTools.ttLib import TTFont
font = TTFont("cipher.ttf")
cmap = font.getBestCmap()

# 按编码顺序，筛出字形名是 ASCII 的项——藏的话就在这里
for cp, name in sorted(cmap.items()):
    if name.isascii():
        print(hex(cp), repr(name))