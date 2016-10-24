import numpy as np
import cv2
import os
from time import gmtime, strftime

MED_FILT = 5
UPDATE_RATE = 500 #Update rate in milliseconds.
SE_DILATE = 20 # Open structuring element 
SE_ERODE = 3
MIN_WIDTH = 70
MIN_HEIGHT = 70
MAX_FILES  = 100

if os.name == 'posix':
    print("Yeay we're in the pie...")
    ONPI = True
else:
    print ("Booo, still in windows...")
    ONPI = False

folder_name = "./Captured/" + strftime("%Y-%m-%d_%H-%M-%S", gmtime()) + "/"
#folder_name = "./Captured/Fred/"
print(folder_name)
os.makedirs(folder_name, 0755)


#Snap the first image to pre-load.
cap = cv2.VideoCapture(0)
ret ,frame = cap.read()
if ret==False:
	print("Error: Could not connect to the camera, exiting!")
	exit()
gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
gray_med = cv2.medianBlur(gray,MED_FILT)
cv2.imshow('Gray',gray)

file_num = 0

while(1):
	ret ,frame = cap.read()
	if ret==True:
		#get the latest image.
		last_gray = gray_med
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		gray_med = cv2.medianBlur(gray,MED_FILT)
		#gray_med = gray
		cv2.imshow('Gray',gray_med)
		
		#Get the subtracted image.
		diff = cv2.subtract(gray, last_gray)
		#cv2.imshow('Diff', diff)
		
		#Threshold.
		ret, bin_diff = cv2.threshold(diff, 20, 255, cv2.THRESH_BINARY)
		#cv2.imshow('BinDiff', bin_diff)
		
		#Morphological erosion.
		SE = np.ones((SE_ERODE, SE_ERODE), np.uint8)
		eroded = cv2.erode(bin_diff, SE, iterations = 1)
		
		#Morphological dilated.
		SE = np.ones((SE_DILATE, SE_DILATE), np.uint8)
		dilated = cv2.dilate(eroded, SE, iterations = 1)
		
		#4-connected component.
		cc = cv2.connectedComponentsWithStats(dilated, 4, cv2.CV_32S)
		
		num_labels = cc[0]
		labels = cc[1]
		stats = cc[2]
		centroids = cc[3]
		
		trig = 0
		trig_lab = 0
		if num_labels > 0:
			for i in range (1, num_labels):
				if (stats[i,cv2.CC_STAT_WIDTH] > MIN_WIDTH) &  (stats[i,cv2.CC_STAT_HEIGHT] > MIN_HEIGHT):
					trig = 1
					trig_lab = i
					print ("Width, Height: ", stats[i,cv2.CC_STAT_WIDTH], stats[i,cv2.CC_STAT_HEIGHT])
					print (dilated)

		if trig > 0:
			x = stats[trig_lab, cv2.CC_STAT_LEFT]
			y = stats[trig_lab, cv2.CC_STAT_TOP]
			w = stats[trig_lab, cv2.CC_STAT_WIDTH]
			h = stats[trig_lab, cv2.CC_STAT_HEIGHT]
			out_im = cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)
			cv2.imshow("Output", out_im)
			if file_num < MAX_FILES:
				file_name = folder_name + "%03d.jpg" %file_num
				print ("Writing to: ", file_name)
				cv2.imwrite(file_name, out_im)
				file_num += 1
			else:
				print ("Folder full!!!")
		#print(num_labels,labels, stats, centroids)
		
		k = cv2.waitKey(UPDATE_RATE) & 0xff
		if k == ord('q'):
			print ("Exiting")
			break

cv2.destroyAllWindows()
cap.release()
