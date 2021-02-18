import cv2 as cv
import numpy as np


# Initialize the parameters
confThreshold = 0.5  #Confidence threshold
nmsThreshold = 0.4  #Non-maximum suppression threshold

inpWidth = 416  #608     #Width of network's input image
inpHeight = 416 #608     #Height of network's input image

# Load names of classes
classesFile = "classes.names";

classes = None
with open(classesFile, 'rt') as f:
    classes = f.read().rstrip('\n').split('\n')

# Give the configuration and weight files for the model and load the network using them.

modelConfiguration = "darknet-yolov3.cfg";
modelWeights = "lapi.weights";

net = cv.dnn.readNetFromDarknet(modelConfiguration, modelWeights)
net.setPreferableBackend(cv.dnn.DNN_BACKEND_OPENCV)
net.setPreferableTarget(cv.dnn.DNN_TARGET_CPU)

# Get the names of the output layers
def getOutputsNames(net):
    # Get the names of all the layers in the network
    layersNames = net.getLayerNames()
    # Get the names of the output layers, i.e. the layers with unconnected outputs
    return [layersNames[i[0] - 1] for i in net.getUnconnectedOutLayers()]


# Remove the bounding boxes with low confidence using non-maxima suppression
def postprocess(frame, outs):
    frameHeight = frame.shape[0]
    frameWidth = frame.shape[1]

    classIds = []
    confidences = []
    boxes = []
    # Scan through all the bounding boxes output from the network and keep only the
    # ones with high confidence scores. Assign the box's class label as the class with the highest score.
    classIds = []
    confidences = []
    boxes = []
    for out in outs:
#        print("out.shape : ", out.shape)
        for detection in out:
            #if detection[4]>0.001:
            scores = detection[5:]
            classId = np.argmax(scores)
            #if scores[classId]>confThreshold:
            confidence = scores[classId]
#            if detection[4]>confThreshold:
#                print(detection[4], " - ", scores[classId], " - th : ", confThreshold)
#                print(detection)
            if confidence > confThreshold:
                center_x = int(detection[0] * frameWidth)
                center_y = int(detection[1] * frameHeight)
                width = int(detection[2] * frameWidth)
                height = int(detection[3] * frameHeight)
                left = int(center_x - width / 2)
                top = int(center_y - height / 2)
                classIds.append(classId)
                confidences.append(float(confidence))
                boxes.append([left, top, width, height])

    # Perform non maximum suppression to eliminate redundant overlapping boxes with
    # lower confidences.
    indices = cv.dnn.NMSBoxes(boxes, confidences, confThreshold, nmsThreshold)
    for i in indices:
        i = i[0]
        box = boxes[i]
        left = box[0]
        top = box[1]
        width = box[2]
        height = box[3]
        return left, top, left + width, top + height


def man(image):

     if (image):
         cap = cv.VideoCapture(image)

     while cv.waitKey(1) < 0:

         # get frame from the video
         hasFrame, frame = cap.read()

         # Create a 4D blob from a frame.
         blob = cv.dnn.blobFromImage(frame, 1/255, (inpWidth, inpHeight), [0,0,0], 1, crop=False)

         # Sets the input to the network
         net.setInput(blob)

         # Runs the forward pass to get output of the output layers
         outs = net.forward(getOutputsNames(net))

         # Remove the bounding boxes with low confidence
         quad = postprocess(frame, outs)
         return quad



##### -----easyocr----- #####
def easy(img):
	import easyocr
	reader = easyocr.Reader(['en'], gpu=False)
	allowlist = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-'

	return reader.readtext(img, paragraph=True, allowlist = allowlist)


def det_rec(img):
    res = man(img)
    if (res!=None):
        img = cv.imread(img)
        roi = img[res[1]:res[3], res[0]:res[2]]
        result = easy(roi)
        if (result!=None and len(result)>0):
            return result[0][1]
        else:
            print('Could not recognize number!')
            
            
##### -----sending message----- #####

MAILGUN_API_KEY = '82794e0e6ee3705196261dd2021e839f-95f6ca46-1e669ab3'
SANDBOX_URL= "sandbox2aa484244180481b8a1ed9e8c4507522.mailgun.org"
SENDER_EMAIL = 'test@' + SANDBOX_URL
RECIPIENT_EMAIL ='anuranjan.m.b@gmail.com'

SID = 'AC1792d98675f0f7c9101f646c1c7fd6f3'
AUTH_TOKEN = '1c5bfda596322c192f3154be64f22b95'
FROM_NUMBER = '+12283358007'
TO_NUMBER = '+919962207957'

import json, requests
from boltiot import Email, Sms

def sndMsg(number):
    try:
        print("Making request to Mailgun to send an email")
        response = mailer.send_email("Alert", "The vehicle number "+number+" has been spotted")
        response_text = json.loads(response.text)
        print("Response received from Mailgun is: " + str(response_text['message']))
    except Exception as e:
        print ("Error occured: Below are the details")
        print (e)
 
def sndMail(number):
    try:
        print("Making request to Twilio to send a SMS")
        response = sms.send_sms("The vehicle number "+number+" has been spotted")
        print("Response received from Twilio is: " + str(response))
        print("Status of SMS at Twilio is :" + str(response.status))
    except Exception as e:
        print ("Error occured: Below are the details")
        print (e)
        
mailer = Email(MAILGUN_API_KEY, SANDBOX_URL, SENDER_EMAIL, RECIPIENT_EMAIL)
sms = Sms(SID, AUTH_TOKEN, TO_NUMBER, FROM_NUMBER)

number=det_rec('images/fc2.jpg')
print(number)
req=requests.get("https://g3fuzkn3g0.execute-api.us-east-1.amazonaws.com/sazar/details").json()
for item in req:
    if (item['nid']==number):
        if(item['blacklisted']==True):
            sndMsg(number)
            sndMail(number)
            
            
            
