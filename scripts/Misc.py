
str1 = "nine Bird nine nine nine Bird Bird nine nine Bird Bird nine Bird Bird nine nine nine Bird Bird nine nine nine nine Bird nine Bird Bird nine nine Bird Bird Bird nine nine Bird Bird nine nine Bird nine nine nine Bird Bird Bird nine Bird nine nine nine Bird nine nine nine nine nine nine Bird nine Bird Bird Bird Bird Bird nine Bird nine Bird nine nine Bird Bird nine Bird Bird nine Bird Bird Bird Bird nine Bird nine Bird Bird Bird Bird Bird nine Bird nine nine nine Bird Bird Bird nine Bird Bird nine Bird Bird Bird Bird nine nine Bird Bird nine nine nine nine nine Bird Bird nine nine Bird nine nine nine Bird Bird nine nine Bird nine nine nine Bird Bird nine nine Bird nine nine nine Bird Bird nine nine Bird nine nine"
str1 = str1.replace("nine" , "0")
str1 = str1.replace("Bird" , "1")
str1 = str1.replace(" ", "")
num1 = int(str1 , 2)
result = ""
for i in range(0, len(str1), 8):
    chunk = str1[i:i+8]
    # 二进制转十进制，再转ascii字符
    ascii_num = int(chunk, 2)
    result += chr(ascii_num)
print(result)

