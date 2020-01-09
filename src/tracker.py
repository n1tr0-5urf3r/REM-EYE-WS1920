import cv2


class Tracker:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')
        self.camera = None
        self.rate = .080
        self.eye_imgs = []

    def take_picture(self):
        """
        Takes a picture with the first available cam
        :return: the image object as ndarray
        """
        if not self.camera:
            self.camera = cv2.VideoCapture(0)
        return_value, image = self.camera.read()
        return image

    def cut_eyebrows(self, img_eye):
        """
        Removes the first quarter of height of image and the lower fifth. Smoothens the image with the median filter.
        :param img_eye:
        :return:
        """
        height = img_eye.shape[0]
        width = img_eye.shape[1]
        img_eye = img_eye[int(0.25 * height):int(0.8 * height), 0:width]
        img_eye = cv2.medianBlur(img_eye, 3)
        return img_eye

    def convert_to_grey(self, img):
        """
        Converts a picture to grayscale
        :param img: The image object
        :return: A grey image object
        """
        grey_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return grey_img

    def get_face_with_eyes(self, img):
        """
        Draws rectangles where face and eyes are recognized
        :return: The image object,of the first detected left eye, None if no face or left eyes detected
        """

        grey_img = self.convert_to_grey(img)
        faces = self.face_cascade.detectMultiScale(grey_img, 1.3, 5)

        for (x, y, w, h) in faces:
            self.eye_imgs = []
            found_eyes_left = []
            found_eyes_right = []
            area_face = w * h
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 0), 2)
            # Cut face out
            grey_face = grey_img[y:y + h, x:x + w]
            face = img[y:y + h, x:x + w]
            eyes = self.eye_cascade.detectMultiScale(grey_face)
            for (ex, ey, ew, eh) in eyes:
                # Only accept eyes in the upper half of detected face, eyes bigger than 1/5 of face are not valid
                # also eyes have to be in the first quarter of face or in the second half
                area_eye = ew * eh
                if ey < h / 3 and area_eye <= 1 / 5 * area_face and (ex <= w / 4 or ex >= 2 * w / 4):
                    # Maybe check for amount of found eyes here?
                    # size of detected eyes should not exceed percentage of complete area of face
                    # Use grey face to cut out eyes for later processing
                    eye = grey_face[ey:ey + eh, ex:ex + ew]
                    if ex < w / 2:
                        found_eyes_left.append(eye)
                        cv2.rectangle(face, (ex, ey), (ex + ew, ey + eh), (0, 128, 0), 2)
                    else:
                        found_eyes_right.append(eye)
                        cv2.rectangle(face, (ex, ey), (ex + ew, ey + eh), (0, 225, 255), 2)
                    self.eye_imgs.append(eye)
                else:
                    # Only for debugging, not needed, displays red rectangle for invalid eyes
                    cv2.rectangle(face, (ex, ey), (ex + ew, ey + eh), (0, 0, 255), 2)
            cv2.imshow("Debug", img)
            cv2.waitKey(10)
            if found_eyes_left:
                cv2.imwrite("img/gsicht.png", img)
                cv2.imwrite("img/auge.png", found_eyes_left[0])
                return found_eyes_left[0]
            else:
                return None

    def adapt_size(self, img1, img2):
        """
        Upscaling to bigger image
        :param img1:
        :param img2:
        :return: tuple of both images
        """
        if img1.shape[0] < img2.shape[0]:
            img1 = cv2.resize(img1, (img1.shape[1], img2.shape[0]), interpolation=cv2.INTER_AREA)
        else:
            img2 = cv2.resize(img2, (img2.shape[1], img1.shape[0]), interpolation=cv2.INTER_AREA)

        if img1.shape[1] < img2.shape[1]:
            img1 = cv2.resize(img1, (img2.shape[1], img1.shape[0]), interpolation=cv2.INTER_AREA)
        else:
            img2 = cv2.resize(img2, (img1.shape[1], img2.shape[0]), interpolation=cv2.INTER_AREA)
        return (img1, img2)
