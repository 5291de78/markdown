# MISC签到题

YulinSec{Mi_H0_Yo_is_So_Go0ddddGenshinHonkaiStarrailZZZ}

用随波逐流CTF编码工具修改这张图片的高发现第一段flag:

`Mi_H0_Yo_is`

再用msys2 用 tesseract（OCR）提取图片文字:

`strings flag.png`

得到第二段flag:

`_So_Go0dddd`

第三段flag就用stegsolve进行扫描，最后发现一张火星文图片，但是将他倒置以后发现还是可以将他看成英文的，简单翻译后得到

`GenshinHonkaiStarrailZZZ`

用了其他很多办法，没有发现其他flag，拼接提交AC。



