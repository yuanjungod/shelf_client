# -*- coding: utf-8 -*-
import numpy as np
import urllib
import cv2

# url = "http://10.12.3.65/resources/slots_theme/theme98/1.png"
url = "http://192.168.1.13:8888/cars/Aston-one-77.png"
resp = urllib.urlopen(url)
image = np.asarray(bytearray(resp.read()), dtype="uint8")
print image
image = cv2.imdecode(image, cv2.IMREAD_COLOR)
cv2.imshow('URL2Image', image)
cv2.waitKey()



