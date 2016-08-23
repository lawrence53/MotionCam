import numpy
print numpy.__version__
import cv2

print ("Hello")
print cv2.__version__

MED_FILT = 5
UPDATE_RATE = 500 #Update rate in milliseconds.

#Snap the first image to pre-load.
cap = cv2.VideoCapture(0)
ret ,frame = cap.read()
gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
gray_med = cv2.medianBlur(gray,MED_FILT)
cv2.imshow('Gray',gray)

while(1):
	ret ,frame = cap.read()
	if ret==True:
		#get the latest image.
		last_gray = gray_med
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		gray_med = cv2.medianBlur(gray,MED_FILT)
		cv2.imshow('Gray',gray_med)
		
		#Get the subtracted image.
		diff = cv2.subtract(gray, last_gray)
		cv2.imshow('Diff', diff)
		
		#Threshold
		ret, bin_diff = cv2.threshold(diff, 20, 255, cv2.THRESH_BINARY)
		cv2.imshow('BinDiff', bin_diff)
		
		k = cv2.waitKey(UPDATE_RATE) & 0xff
		if k == ord('q'):
			print ("Exiting")
			break

cv2.destroyAllWindows()
cap.release()