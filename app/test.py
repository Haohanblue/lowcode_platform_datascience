from cnocr import CnOcr

img_fp = './docs/QQ截图20240912111746.png'
ocr = CnOcr()  # 所有参数都使用默认值
out = ocr.ocr(img_fp)

print(out)