import cv2
import time
import pygame
from node import Node
from button import Button
import numpy as np


class App:
    def __init__(self, tracker):
        # Pygame stuff
        pygame.init()
        infoObject = pygame.display.Info()
        self.screen_width = infoObject.current_w
        self.screen_height = infoObject.current_h
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.screen = self.screen.convert_alpha()
        self.small_font = pygame.font.SysFont('Arial', 15)
        self.medium_font = pygame.font.SysFont('Arial', 15)
        self.big_font = pygame.font.SysFont('Arial', 50)
        # Tracker object
        self.tracker = tracker
        # Stores the most recent gazing coords
        self.gaze_coords = []
        # Needed because of slow cameras (apple), adjust to brightness
        self.camera_opening_time = .5
        # Used to control the main loop
        self.started_calibration = False
        self.started_tracking = False
        self.running = True

        self.width_adapt = self.screen_width - 40
        self.height_adapt = self.screen_height - 130
        # Defining keypoint calibration section
        k1 = Node(int(self.width_adapt / 2), 10)
        k2 = Node(int(self.width_adapt / 4), int(self.height_adapt / 4))
        k3 = Node(int(self.width_adapt / 2), int(self.height_adapt / 2))
        k4 = Node(3 * int(self.width_adapt / 4), int(self.height_adapt / 4))
        k5 = Node(self.width_adapt, self.height_adapt)
        k6 = Node(int(self.width_adapt / 2), self.height_adapt)
        k7 = Node(int(self.width_adapt / 4), 3 * int(self.height_adapt / 4))
        k8 = Node(10, int(self.height_adapt / 2))
        k9 = Node(self.width_adapt, int(self.height_adapt / 2))
        k10 = Node(10, self.height_adapt)
        k11 = Node(3 * int(self.width_adapt / 4), 3 * int(self.height_adapt / 4))
        k12 = Node(self.width_adapt, 10)
        k13 = Node(10, 10)

        # set the neighbor nodes
        k1.neighbors = [k13, k2, k3, k4, k12]
        k2.neighbors = [k13, k1, k3, k7, k8]
        k3.neighbors = [k1, k2, k4, k7, k11, k6]
        k4.neighbors = [k1, k3, k12, k9, k11]
        k5.neighbors = [k6, k11, k9]
        k6.neighbors = [k10, k7, k3, k11, k5]
        k7.neighbors = [k8, k2, k3, k6, k10]
        k8.neighbors = [k13, k2, k7, k10]
        k9.neighbors = [k12, k4, k11, k5]
        k10.neighbors = [k8, k7, k6]
        k11.neighbors = [k6, k3, k4, k9, k5]
        k12.neighbors = [k1, k4, k9]
        k13.neighbors = [k8, k2, k1]

        self.keypoints = [k1, k2, k3, k4, k5, k6, k7, k8, k9, k10, k11, k12, k13]
        self.found_calibrations = 0
        self.counter = 0

    def draw_nodes(self):
        """ Draws the calibration nodes in their respective color and their neighbor connections"""
        for node in self.keypoints:
            pygame.draw.circle(self.screen, node.color, (node.x, node.y), 15)
            for n in node.neighbors:
                pygame.draw.line(self.screen, node.color, (node.x, node.y), (n.x, n.y))

    def draw_multiline_text(self, text):
        """
        Draws a multiline text in the center of the screen
        :param text: a list of lines to be drawn
        """
        counter = 0
        for line in text:
            textsurface = self.big_font.render(line, False, (255, 255, 255))
            self.screen.blit(textsurface,
                             (int(self.screen_width / 2) - 500, int(self.screen_height / 2) + counter * 60 - 300))
            counter += 1

    def loop_gui(self):
        """
        The main loop, starts calibration and tracking routine
        """

        def reset_node_colors():
            """Resets all node's color to white"""
            for node in self.keypoints:
                node.color = (255, 255, 255)

        welcome_text = ["Hallo, folge dem Button mit deinen Augen und klicke darauf,",
                        "willst du abbrechen, so drücke auf 'quit'",
                        "Bereit? Dann klick auf 'Los!'"]
        feedback_text = ["Klicke und schaue dabei auf den Button!"]
        x = self.keypoints[0].x
        y = self.keypoints[0].y
        while self.running:
            self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
            mouse = pygame.mouse.get_pos()
            click = pygame.mouse.get_pressed()
            if not self.started_calibration:
                # Welcome screen
                self.draw_multiline_text(welcome_text)
                button_go = Button(int(self.screen_width / 2), int(self.screen_height / 2), "Los!", self.screen, 150,
                                   100, (0, 0, 255))
                button_quit = Button(int(self.screen_width / 2), int(self.screen_height / 2) + 150, "Quit!",
                                     self.screen, 150, 100, (0, 0, 255))
                if button_go.button_clicked(click, mouse, (0, 255, 255)):
                    self.started_calibration = True
                elif button_quit.button_clicked(click, mouse, (0, 255, 255)):
                    self.running = False
                    pygame.quit()
                    quit()
            elif self.started_calibration and not self.started_tracking:
                self.draw_multiline_text(feedback_text)
                # Change color of current node to red and redraw it
                self.keypoints[self.counter].color = (255, 0, 0)
                self.draw_nodes()
                # Draw button to the left of node if we're on the right side of the screen
                if x == self.width_adapt:
                    calib_button = Button(x - 100, y, "Click me!", self.screen, 100, 50, (255, 0, 0))
                else:
                    calib_button = Button(x, y, "Click me!", self.screen, 100, 50, (255, 0, 0))
                if calib_button.button_clicked(click, mouse, (255, 102, 102)):
                    # Take picture here and save coordinates
                    new_coords = self.take_calibration_point()
                    self.keypoints[self.counter - 1].color = (0, 255, 0)
                    old_x = x
                    old_y = y
                    x = new_coords[0]
                    y = new_coords[1]
                    if old_x == x and old_y == y:
                        # If both, old and new, coords are the same it means we reached the last keypoint
                        # Stop calibration and start tracking
                        self.started_tracking = True
                    else:
                        feedback_text = ["Kalibrierung {} gespeichert!".format(self.counter)]
            else:
                if not list(self.gaze_coords):
                    # First tracking, nothing to compare, just save
                    self.gaze_coords = self.start_tracking()
                else:
                    gaze_coords_new = self.start_tracking()
                    # set the gazing point to the new position, if its accurate
                    if gaze_coords_new:
                        if gaze_coords_new != [0, 0]:
                            self.gaze_coords = gaze_coords_new
                            pygame.draw.circle(self.screen, (255, 0, 0),
                                               (int(self.gaze_coords[0]), int(self.gaze_coords[1])), 5, 5)
                    else:
                        pygame.draw.circle(self.screen, (255, 0, 0),
                                           (int(self.gaze_coords[0]), int(self.gaze_coords[1])), 5, 5)
                self.draw_nodes()
                reset_node_colors()
            pygame.display.update()

    def take_calibration_point(self):
        """
        Takes three pictures on the current calibration point and saves it to node object
        Repeats take_picture() until 3 valid pictures are saved
        :return: list of x and y coordianates of current node
        """
        x = self.keypoints[self.counter].x
        y = self.keypoints[self.counter].y
        # check whether all calibration pictures are already taken
        if self.found_calibrations < 3 * len(self.keypoints):
            found_calibration_for_node = 0
            while found_calibration_for_node < 3:
                # take picture
                # Detects eyes and stores them in tracker class variable eye_imgs
                # Take pictures until eye is recognized
                cam = cv2.VideoCapture(0)
                time.sleep(self.camera_opening_time)
                return_value, image = cam.read()
                # Detect eye
                eye_left = self.tracker.get_face_with_eyes(image)
                # Debugigng
                cv2.imshow("DEBUG", image)
                cv2.waitKey(10)
                # cv2.destroyAllWindows()
                # If eye is found, save and process it
                try:
                    if list(eye_left):
                        # Cut eyebrows
                        eye_left = self.tracker.cut_eyebrows(eye_left)
                        # insert new picture with matching coordinates x and y in form of a dictionary in the Array
                        self.keypoints[self.counter].image.append(eye_left)
                        self.found_calibrations += 1
                        found_calibration_for_node += 1
                        time.sleep(1)
                        # increment counter in order to consider next keypoint
                        if self.counter < len(self.keypoints) - 1 and found_calibration_for_node == 3:
                            self.counter += 1
                            # move the button to the next position
                            x = self.keypoints[self.counter].x
                            y = self.keypoints[self.counter].y
                    cam.release()
                except TypeError:
                    print("DEBUG: No face/eye detected")
                    cam.release()
                    pass
        else:
            self.started_tracking = True
        return [x, y]

    def start_tracking(self):
        """
        Starts the tracking routine, takes a picture and detects eyes in it. Calculates the similarities afterwards
        :return: new coordinates of gazing point, None if no eyes are found
        """
        tracker = self.tracker
        try:
            # Take an image and save it
            image = tracker.take_picture()
            # Recognize face and eyes
            tracker.get_face_with_eyes(image)
            # Get detected eyes from tracker
            if tracker.eye_imgs:
                # Cut eyebrows
                eye_left = tracker.cut_eyebrows(tracker.eye_imgs[0])
                if list(eye_left):
                    # get the similarity between the taken picture and the template pictures of the calibration
                    similarities = self.create_diff_array(eye_left)
                    # calculate the new coordinates of the gazing point
                    positions = self.interpolate(similarities)
                    time.sleep(tracker.rate)
                    return positions
            # Skip image if no face/eyes detected
            time.sleep(tracker.rate)
            return None
        except KeyboardInterrupt:
            # Gratefully close everything
            tracker.camera.release()
            cv2.destroyAllWindows()
            self.running = False

    def print_calibration(self):
        """
        Opens all calibrated images and their coordinates, used for debugging
        """
        for point in self.keypoints:
            x = point.x
            y = point.y
            for i in point.image:
                cv2.imshow("X: {}, Y: {}".format(x, y), i)
                cv2.waitKey(0)
                cv2.destroyAllWindows()

    def create_diff_array(self, pic1):
        """
        Compares the given image with all template images of the calibration. Checks for accuracy of the given image
        by checking the relation of the three best matching nodes.
        :param pic1: The current eye image
        :return: Array of the three best matches, each element contains a dictionary with additional information about
        the matching node and the similarity between pic1 and the template image of the node.
        """
        diff_array = []
        counter = 0
        # get the best match of pic 1 with the three template images of each calibration point
        for point in self.keypoints:
            # ------------- Hog feature compare ---------------
            comp1 = self.compare_hog(pic1, point.image[0])
            comp2 = self.compare_hog(pic1, point.image[1])
            comp3 = self.compare_hog(pic1, point.image[2])
            # get the maximum of the similarities
            self.comp = sorted([comp1, comp2, comp3])[0]
            diff_array.append({"similarity": self.comp, "img_index_keypoints": counter, "node": point})
            counter += 1
        # sort the array of the best matches according to the trait "similarity"
        diff_array = sorted(diff_array, key=lambda i: i['similarity'], reverse=False)
        # rescale the trait "similarity", higher scores mean better match
        max = diff_array[5]["similarity"]
        for element in diff_array:
            element["similarity"] = 1 - element["similarity"] / max
        # test for neighboring nodes, if one isn't a neighbor of the other ones, set corresponding "similarity" to 0
        if diff_array[1]["node"] in diff_array[0]["node"].neighbors:
            if diff_array[2]["node"] in diff_array[0]["node"].neighbors:
                pass
            elif diff_array[2]["node"] not in diff_array[0]["node"].neighbors:
                diff_array[2]["similarity"] = 0
        if diff_array[2]["node"] in diff_array[0]["node"].neighbors:
            if diff_array[1]["node"] in diff_array[0]["node"].neighbors:
                pass
            elif diff_array[1]["node"] not in diff_array[0]["node"].neighbors:
                diff_array[1]["similarity"] = 0
        if diff_array[1]["node"] not in diff_array[0]["node"].neighbors:
            if diff_array[0]["node"] not in diff_array[2]["node"].neighbors:
                diff_array[0]["similarity"] = 0
                diff_array[1]["similarity"] = 0
                diff_array[2]["similarity"] = 0
        return [diff_array[0], diff_array[1], diff_array[2]]

    def compare_hog(self, pic1, pic2):
        """
        Compares hog features of two pictures
        :param pic1:
        :param pic2:
        :return: the absolute euclidean distance of both hog feature vectors
        """
        # Scale images to same dimensions
        pic1, pic2 = self.tracker.adapt_size(pic1, pic2)
        cell_size = (8, 8)  # h x w in pixels
        block_size = (2, 2)  # h x w in cells
        nbins = 9  # number of orientation bins
        hog = cv2.HOGDescriptor(_winSize=(pic1.shape[1] // cell_size[1] * cell_size[1],
                                          pic1.shape[0] // cell_size[0] * cell_size[0]),
                                _blockSize=(block_size[1] * cell_size[1],
                                            block_size[0] * cell_size[0]),
                                _blockStride=(cell_size[1], cell_size[0]),
                                _cellSize=(cell_size[1], cell_size[0]),
                                _nbins=nbins)

        hog_feats_eye1 = hog.compute(pic1)
        hog_feats_eye2 = hog.compute(pic2)  # index blocks by rows first

        if not list(hog_feats_eye1) or not list(hog_feats_eye2):
            # return very high value to ignore this keypoint because hog calculation went wrong
            return 1000
        dist = abs(np.linalg.norm(hog_feats_eye1 - hog_feats_eye2))
        return dist

    def interpolate(self, best3):
        """
        interpolates between the three most accurate positions in keypoint coordinates based on the trait "similarity" ,
        changes the colour of the corresponding nodes
        :param best3: array of the three best matches between the current image and the template images
        :return: new coordinates of gazing point
        """

        def set_node_color(node, similarity):
            if similarity == 0:
                # Red node if node will not be used for interpolation
                node.color = (255, 0, 0)
            else:
                # Green node else
                node.color = (0, 255, 0)

        # get the informations of the best matching node
        first = best3[0]
        first_index = first["img_index_keypoints"]
        first_similarity = first["similarity"]
        first_x = self.keypoints[first_index].x
        first_y = self.keypoints[first_index].y
        # get the informations of the second best matching node
        second = best3[1]
        second_similarity = second["similarity"]
        second_index = second["img_index_keypoints"]
        second_x = self.keypoints[second_index].x
        second_y = self.keypoints[second_index].y
        # get the informations of the third best matching node
        third = best3[2]
        third_similarity = third["similarity"]
        third_index = third["img_index_keypoints"]
        third_x = self.keypoints[third_index].x
        third_y = self.keypoints[third_index].y
        # change the colour of the node
        set_node_color(self.keypoints[first_index], first_similarity)
        set_node_color(self.keypoints[second_index], second_similarity)
        set_node_color(self.keypoints[third_index], third_similarity)
        # calculate the weighted average of the three coordinates, according to the trait "similarity"
        sum_similarities = first_similarity + second_similarity + third_similarity
        if sum_similarities != 0:
            x = int((
                            first_similarity * first_x + second_similarity * second_x + third_similarity * third_x) / sum_similarities)
            y = int((
                            first_similarity * first_y + second_similarity * second_y + third_similarity * third_y) / sum_similarities)
        else:
            x = 0
            y = 0
        return [x, y]
