import cv2
import pickle
import keyboard

width, height = 90, 120
font = cv2.FONT_HERSHEY_SIMPLEX
font_scale = 0.8
color = (255, 255, 255)
thickness = 1



try:
    with open('CarParkPos', 'rb') as f:
        posList = pickle.load(f)
except:
    posList = []


def mouseClick(events, x, y, flags, params):
    if events == cv2.EVENT_LBUTTONDOWN:
        posList.append((x, y,width,height))
    if events == cv2.EVENT_RBUTTONDOWN:
        for i, pos in enumerate(posList):
            x1, y1,w1,h1 = pos
            if x1 < x < x1 + w1 and y1 < y < y1 + h1:
                posList.pop(i)

    with open('CarParkPos', 'wb') as f:
        pickle.dump(posList, f)

def key_pressed(event):
    global width, height
    if event.name == 'up':
        height += 1
    elif event.name == 'down':
        height -= 1
    elif event.name == 'left':
        width -= 1
    elif event.name == 'right':
        width += 1

# Bind the key_pressed function to keyboard events
keyboard.on_press(key_pressed)






while True:
    img = cv2.imread('carParkImg.png')
    for index,pos in enumerate(posList):#pos[2] is width pos[3] is height
        cv2.rectangle(img, (pos[0], pos[1]), (pos[0] + pos[2], pos[1] + pos[3]), (255, 0, 255), 2)
        # Calculate the position to place the number text
        text_pos = (pos[0] + 10, pos[1] + pos[3] - 10)  # Adjust the position as needed

        # Draw the number attribute on the image
        cv2.putText(img, str(index), text_pos, font, font_scale, color, thickness)


    cv2.imshow("Image", img)
    cv2.setMouseCallback("Image", mouseClick)
    cv2.waitKey(1)