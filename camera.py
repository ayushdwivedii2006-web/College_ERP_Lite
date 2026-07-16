import cv2

camera = cv2.VideoCapture(0)

while True:

    success, frame = camera.read()

    if not success:
        break

    cv2.imshow("College ERP AI Camera", frame)

    key = cv2.waitKey(1)

    if key == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()