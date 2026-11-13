import base64
from fontTools.ttLib import TTFont

file_name = input("Enter file name: ")
if file_name == "1":

with open("bs64.txt", "r") as file:
    b64 = file.read()
open("cipher.ttf", "wb").write(base64.b64decode(b64))
font = TTFont("cipher.ttf")
cmap = font.getBestCmap()
with open("cipher.txt", "w") as file:
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


font = TTFont("cipher.ttf")
cmap = font.getBestCmap()

# 按编码顺序，筛出字形名是 ASCII 的项——藏的话就在这里
for cp, name in sorted(cmap.items()):
    if name.isascii():
        print(hex(cp), repr(name))