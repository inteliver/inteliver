"""
    ImageProcessor class

    This class is responsible for processing an image and apply
        machine learning and A.I. algorithms on images.
"""

import cv2
import dlib
import numpy as np

#  from app.image.object_detection import ObjectDetection


class ImageProcessor:
    """
    ImageProcessor class

    This class is responsible for processing an image and apply
        machine learning and A.I. algorithms on images.

    Attributes:
        _face_detector (dlib.object): dlib default face detector.

    Methods:
        get_commands(self): Loop over subcommands attribute and
            yeilds each subcommand.

    """

    _face_detector = dlib.get_frontal_face_detector()
    # _object_detector = ObjectDetection()
    _object_detector = None

    def __init__(self):
        """
        ImageProcessor __init__ method

        This function initializes the ImageProcessor object and set the
            command_processors dictionary, operator_processors dictionary
            and mask_processors dictionary. Each dictionary is consist of
            different commands and their corrosponding function.

        Attributes:
            _face_detector (dlib.object): dlib default face detector.

        """

        # select window dictionary
        # select_window[0] = select_window['width']
        # select_window[1] = select_windo['height']
        self.select_window = {"height": None, "width": None}
        # For multiple window selectors like face
        self.select_windows = []
        # [x, y]
        # gravity[0] = gravity['x']
        # gravity[1] = gravity['y']
        self.gravity = {"x": None, "y": None}
        self.image = None
        self.format = "image/jpeg;q=0.95"
        self.command_processors = {}
        self.operator_processors = {}
        self.mask_processors = {}
        self._init_command_processors()
        self._init_operator_processors()
        self._init_mask_processors()

    def _init_command_processors(self):
        """
        ImageProcessor _init_command_processors method

        It will set the command_processor dictionary. This dictionary
            is consist of selectors base command and their corosponding
            method pair.

        """

        self.command_processors["i_h_"] = self.selector_height
        self.command_processors["i_w_"] = self.selector_width
        self.command_processors["i_c_"] = self.selector_center
        self.command_processors["i_m_"] = self.selector_mask
        self.command_processors["i_o_"] = self.modifier_operator

    def _init_mask_processors(self):

        self.mask_processors["skin"] = self.mask_skin
        self.mask_processors["face"] = self.mask_face
        self.mask_processors["sat"] = self.mask_sat
        self.mask_processors["hue"] = self.mask_hue
        self.mask_processors["val"] = self.mask_val

    def _init_operator_processors(self):
        """
        ImageProcessor _init_operator_processors method

        It will set the operator_processors dictionary. This dictionary
            is consist of operators command and their corosponding
            method pair.

        The operator_commands are followed by a 'i_o_' syntax which is
            handeld by command processor and the operator commands specefic
            functions such as 'crop', 'resize', 'format' and etc, are called
            by the operator_processors dictionary.

        """

        self.operator_processors["crop"] = self.operator_crop
        self.operator_processors["resize"] = self.operator_resize
        self.operator_processors["format"] = self.operator_format
        self.operator_processors["blur"] = self.operator_blur
        self.operator_processors["rotate"] = self.operator_rotate
        self.operator_processors["flip"] = self.operator_flip
        self.operator_processors["rcrop"] = self.operator_round_crop
        self.operator_processors["sharpen"] = self.operator_sharpen
        self.operator_processors["pixelate"] = self.operator_pixelate
        self.operator_processors["gray"] = self.operator_gray
        self.operator_processors["text"] = self.operator_text
        self.operator_processors["detect"] = self.operator_object_detection

    def process(self, command, rtype, data):
        """
        ImageProcessor process method

        processes an image and apply basic A.I.
         and machine learning algorithms on image.

        Args:
            command (str): commands string query.

            rtype (str): data type.

            data (numpy.ndarray): image binary data in form of numpy
                ndarray with shape (height, width, 3)

        Returns:
            The return data type and the applied image data
                if successful otherwise error as type and None
                as image binary data.

        """

        self.image = data
        self.image_height = self.image.shape[0]
        self.image_width = self.image.shape[1]

        for cmd in command:
            if cmd[:4] not in self.command_processors:
                return "error/invalid_subcommand", None
            self.command_processors[cmd[:4]](cmd[4:])

        return self.format, self.image

    def _safe_int(self, str, default_val=0):
        ret_val = default_val
        try:
            ret_val = int(str)
        except (ValueError, TypeError):
            pass
        return ret_val

    def _safe_float(self, str, default_val=0.0):
        ret_val = default_val
        try:
            ret_val = float(str)
        except (ValueError, TypeError):
            pass
        return ret_val

    def _arg_value(self, arg_str, multiplier, default=None):
        if "." in arg_str:
            try:
                return multiplier * float(arg_str)
            except (ValueError, TypeError):
                return default
        try:
            return int(arg_str)
        except (ValueError, TypeError):
            return default

    def selector_height(self, height):
        """
        ImageProcessor selector_height method

        This method will set selector_window[1] which is image height to
            image height if 'ih' is used in command instead of height number,
            image width if 'iw' is used in command instead of height number
            or a value which is given after 'ih_'.

        If the height value is an integer then the size will be equal to
            the value, if it is a float number, then the image height will
            be multiplied into that float number.

        Args:
            height (str): Selector string for image height.

        """

        if height == "ih":
            self.select_window["height"] = self.image_height
        elif height == "iw":
            self.select_window["height"] = self.image_width
        else:
            self.select_window["height"] = self._arg_value(
                height, self.image_height, None
            )

    def selector_width(self, width):
        """
        ImageProcessor selector_width method

        This method will set selector_window[0] which is image width to
            image height if 'ih' is used in command instead of width number,
            image width if 'iw' is used in command instead of width number
            or a value which is given after 'iw_'.

        If the width value is an integer then the size will be equal to
            the value, if it is a float number, then the image width will
            be multiplied into that float number.

        Args:
            width (str): Selector string for image width.

        """

        if width == "ih":
            self.select_window["width"] = self.image_height
        elif width == "iw":
            self.select_window["width"] = self.image_width
        else:
            self.select_window["width"] = self._arg_value(width, self.image_width, None)

    def selector_center(self, center):
        """
        ImageProcessor selector_center method

        This method will set gravity of an image based on the center
            required by user command. User can center the operations
            on face or a custom x and y.

        Args:
            center (str): Selector string for image center.

        """

        selector_functions = {
            "x": self.selector_center_x,
            "y": self.selector_center_y,
            "face": self.selector_center_face,
            "object": self.selector_center_object,
        }
        center_segs = center.split("_")
        center = center_segs[0]
        if center in selector_functions:
            selector_functions[center](center_segs)
        if len(center_segs) < 2:
            return

    def selector_center_x(self, center_segs):
        """
        ImageProcessor selector_center_x method

        This method will set gravity of an image based on *x* value.

        Args:
            center_segs (list): Selector string segments for image center.
        """

        if len(center_segs) < 2:
            return
        value = center_segs[1]
        self.gravity["x"] = self._arg_value(value, self.image_width, None)
        if self.gravity["x"] < 0:
            self.gravity["x"] += self.image_width

    def selector_center_y(self, center_segs):
        """
        ImageProcessor selector_center_y method

        This method will set gravity of an image based on *y* value.

        Args:
            center_segs (list): Selector string segments for image center.
        """

        if len(center_segs) < 2:
            return
        value = center_segs[1]

        self.gravity["y"] = self._arg_value(value, self.image_height, None)
        if self.gravity["y"] < 0:
            self.gravity["y"] += self.image_height

    def selector_center_face(self, center_segs):
        """
        ImageProcessor selector_center_face method

        This method will set gravity of an image based on detected face.

        Args:
            center_segs (list): Selector string segments for image center.

        """

        faces = self._face_detector(self.image, 1)
        faces_len = len(faces)
        if faces_len == 0:
            return
        face_idx = 0
        if len(center_segs) > 1:
            face_idx = self._safe_int(center_segs[1], 0)
        if face_idx < 0:
            face_idx = 0
        elif face_idx >= faces_len:
            face_idx = faces_len - 1
        face = faces[face_idx]
        self.gravity["x"] = (face.left() + face.right()) // 2
        self.gravity["y"] = (face.top() + face.bottom()) // 2
        self.select_window["width"] = face.right() - face.left()
        self.select_window["height"] = face.bottom() - face.top()

        for face in faces:
            self.select_windows.append(
                [face.left(), face.top(), face.right(), face.bottom()]
            )

    def selector_center_object(self, center_segs):
        """
        ImageProcessor selector_center_face method

        This method will set gravity of an image based on detected object.

        Args:
            center_segs (list): Selector string segments for image center.

        """
        if len(center_segs) < 2:
            return
        object_name = center_segs[1]
        object_idx = 0
        if len(center_segs) > 3:
            object_idx = int(center_segs[2])
        object_map = self._object_detector.detect_objects_map(self.image)
        if object_name not in object_map:
            return
        detected_objects = object_map[object_name]
        if object_idx < len(detected_objects):
            selected_object = detected_objects[object_idx]
            selected_object["x"] = max(selected_object["x1"], 0)
            selected_object["y"] = max(selected_object["y1"], 0)
            self.gravity["x"] = (selected_object["x1"] + selected_object["x2"]) // 2
            self.gravity["y"] = (selected_object["y1"] + selected_object["y2"]) // 2
            self.select_window["width"] = selected_object["x2"] - selected_object["x1"]
            self.select_window["height"] = selected_object["y2"] - selected_object["y1"]

    def selector_mask(self, mask):
        mask_segs = mask.split("_")
        mask_type = mask_segs[0]
        if mask_type not in self.mask_processors:
            return
        mask_args = "_".join(mask_segs[1:])
        self.mask_processors[mask_type](mask_args)

    def mask_skin(self, args):
        pass

    def mask_face(self, args):
        pass

    def mask_sat(self, args):
        pass

    def mask_hue(self, args):
        pass

    def mask_val(self, args):
        pass

    def modifier_operator(self, operator):
        """
        ImageProcessor modifier_operator method

        This method will be called by command processor if a prefix of
            'i_o_' plus the operator command is used in command query.
            it will apply the specified operator command on image.

        Args:
            operator (str): Operator command such as 'crop', 'resize',
                'format' and etc.

        Returns:
            Nothing if operator command is not recognized, otherwise apply
                the command on image.
        """

        op_segs = operator.split("_")
        op_type = op_segs[0]
        if op_type not in self.operator_processors:
            return

        self.operator_processors[op_type](op_segs[1:])

        # Reset selection window and windows and gravity
        self.select_window = {"height": None, "width": None}
        self.select_windows = []
        self.gravity = {"x": None, "y": None}

    def operator_on_selection(self, op):
        """
        ImageProcessor operator_on_selection method

        This method is responsible for applying an operation command on a
            an image. It will apply it to whole image if select_window or
            gravity contains None. To a selected window if select_window
            and gravity is set. And to multiple windows if select_windows
            is set.

        Args:
            op (function): The operator function to be called on image.

        """

        if None in (
            self.select_window["width"],
            self.select_window["height"],
            self.gravity["x"],
            self.gravity["y"],
        ):
            self.image = op(self.image)
            return

        if len(self.select_windows) == 0:
            x1 = self.gravity["x"] - self.select_window["width"] // 2
            x2 = self.gravity["x"] + self.select_window["width"] // 2
            y1 = self.gravity["y"] - self.select_window["height"] // 2
            y2 = self.gravity["y"] + self.select_window["height"] // 2
            self.image[y1:y2, x1:x2] = op(self.image[y1:y2, x1:x2])

        for window in self.select_windows:
            self.image[window[1] : window[3], window[0] : window[2]] = op(
                self.image[window[1] : window[3], window[0] : window[2]]
            )

    def operator_crop(self, args):
        """
        ImageProcessor operator_crop method

        This method is responsible for croping operation. It will crop image
            based on select_window's height and width ( if height or width is None)
            then original shape will be used.

        It crop the image based on gravity's x and y. If gravity's x or y is
            None the middle of the original shape is considered as gravity for
            that dimension.

        """

        patch_height = (
            self.select_window["height"]
            if self.select_window["height"]
            else self.image_height
        )
        patch_width = (
            self.select_window["width"]
            if self.select_window["width"]
            else self.image_width
        )

        center_x = self.gravity["x"] if self.gravity["x"] else self.image_width // 2
        center_y = self.gravity["y"] if self.gravity["y"] else self.image_height // 2

        # cv2.getRectSubPix only works for images with depth==1 or depth==3
        # here's a hack for images with different depth
        if self.image.shape[2] not in (1, 3):
            layers = cv2.split(self.image)
            self.image = cv2.merge(
                [
                    cv2.getRectSubPix(
                        layer, (patch_width, patch_height), (center_x, center_y)
                    )
                    for layer in layers
                ]
            )
        else:
            self.image = cv2.getRectSubPix(
                self.image, (patch_width, patch_height), (center_x, center_y)
            )

    def operator_resize(self, args):
        """
        ImageProcessor operator_resize method

        This method is responsible for resize operator. new height and
            new weight is calulated by hight and width selectors. if
            select_window's width or height is None then new width or
            height is calculated based on other demension ratio.

        If 'keep' keyword is present in resize command, then the image
            is croped based on the minimum dimension ratio and then resized.

        Args:
            args (str): Extra arguments passed to resize. For example if
                'keep' is sent to resize operator, then the ratio of image
                after resize is kept the same.

        """

        new_height = self.select_window["height"]
        new_width = self.select_window["width"]

        if new_height is None and new_width is None:
            return

        if new_height is None:
            new_height = self._safe_int(
                self.image_height * (new_width / self.image_width)
            )
        elif new_width is None:
            new_width = self._safe_int(
                self.image_width * (new_height / self.image_height)
            )

        if len(args) and args[0] == "keep":
            wr = self.image_width / new_width
            hr = self.image_height / new_height
            ratio = min(wr, hr)
            self.select_window = {
                "width": self._safe_int(ratio * new_width),
                "height": self._safe_int(ratio * new_height),
            }
            self.operator_crop([])

        self.image = cv2.resize(self.image, (new_width, new_height))

    def operator_format(self, args):
        """
        ImageProcessor operator_format method

        This method will be called if a format operator command is used.

        It will change the format and quality of compression to the
            requested user format. default format is 'image/jpeg' and
            default quality is '0.95'.

        Currently only jpeg and png formats are supported.

        Args:
            args (str): Extra arguments passed to format operator. It is
                currently the value of quality of the compression.

        Returns:
            Nothing.

        """

        args_size = len(args)
        if args_size == 0:
            return
        format = "image/jpeg"
        quality = 0.95
        if args[0] == "png":
            format = "image/png"
            if args_size > 1:
                q = self._safe_int(args[1], 3)
                quality = max(0, min(9, q)) / 10.0
            else:
                quality = 0.3
        elif args[0] == "jpg" or args[0] == "jpeg":
            format = "image/jpeg"
            if args_size > 1:
                q = self._safe_int(args[1], 95)
                quality = max(0, min(100, q)) / 100.0
            else:
                quality = 0.95
        elif args[0] == "webp":
            format = "image/webp"
            if args_size > 1:
                q = self._safe_int(args[1], 80)
                quality = max(0, min(100, q)) / 100.0
            else:
                quality = 0.80

        self.format = f"{format};q={quality}"

    def operator_blur(self, args):
        """
        ImageProcessor operator_blur method

        This method is responsible for bluring operation. using
            opencv blur function.

        Args:
            args (str): Extra arguments passed to blure operator. It is
                currently the value of blurring kernel size. default bluring
                kernel size is 3.

        """

        ksize = 3
        if len(args) > 0:
            ksize = self._safe_int(args[0], 3)
            if ksize % 2 == 0:
                ksize += 1

        def do_blur(image):
            return cv2.blur(image, (ksize, ksize))

        self.operator_on_selection(do_blur)

    def operator_rotate(self, args):
        """
        ImageProcessor operator_rotate method

        This method is responsible for rotating operation. using
            opencv getRotationMatrix2D function.

        Args:
            args (str): Extra arguments passed to rotate operator. It is
                currently the value of rotate degree (first arg) and
                rotate scale (second arg).

        """

        if not len(args):
            return

        rot_degree = self._safe_int(args[0], 0)
        if not rot_degree:
            return

        rot_scale = 1.0
        if len(args) > 1:
            rot_scale = self._safe_float(args[1], 1.0)

        center = [self.gravity["x"], self.gravity["y"]]
        if center[0] is None:
            center[0] = self.image_width // 2
        if center[1] is None:
            center[1] = self.image_height // 2
        center = tuple(center)

        dsize = [self.select_window["width"], self.select_window["height"]]
        if dsize[0] is None:
            dsize[0] = self.image_width
        if dsize[1] is None:
            dsize[1] = self.image_height
        dsize = tuple(dsize)

        rot_mat = cv2.getRotationMatrix2D(center, rot_degree, rot_scale)
        self.image = cv2.warpAffine(self.image, rot_mat, dsize)

    def operator_flip(self, args):
        """
        ImageProcessor operator_flip method

        This method is responsible for flipping operation. using
            opencv flip function.

        Args:
            args (str): Extra arguments passed to flip operator. It is
                currently the value of flip direction. 'v', 'h' and 'b'
                is the available values.

        """

        if not len(args):
            return
        rot_codes = {"v": 0, "h": 1, "b": -1}
        rot_code = args[0]
        if rot_code not in rot_codes:
            return
        self.image = cv2.flip(self.image, rot_codes[rot_code])

    def operator_round_crop(self, args):
        """
        ImageProcessor operator_round_crop method

        This method is responsible for round croping operation. using
            opencv ellipse function.

        """

        def do_round_crop(image):
            image_height = image.shape[0]
            image_width = image.shape[1]
            b, g, r = cv2.split(image)
            alpha = np.zeros(b.shape, dtype=b.dtype)
            rows, cols = (image_height, image_width)
            # axes (as well as center) has to be an integers tuple, not floats.
            cv2.ellipse(
                alpha, (cols // 2, rows // 2), (cols // 2, rows // 2), 0, 0, 360, 1, -1
            )
            b = b * alpha
            g = g * alpha
            r = r * alpha
            image = cv2.merge((b, g, r, alpha * 255))
            return image

        self.operator_on_selection(do_round_crop)

    def operator_sharpen(self, args):
        """
        ImageProcessor operator_sharpen method

        This method is responsible for sharpening operation. using
            opencv filter2D function.

        """

        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])

        def do_sharpen(image):
            return cv2.filter2D(image, -1, kernel)

        self.operator_on_selection(do_sharpen)

    def operator_pixelate(self, args):
        """
        ImageProcessor operator_pixelate method

        This method is responsible for pixelating operation. using
            opencv filter2D function.

        Args:
            args (str): Extra arguments passed to pixelate operator. It
                is currently the value of pixel size.

        """

        if len(args) == 0:
            return
        pixel_size = self._safe_int(args[0], 0)
        if pixel_size < 2:
            return

        def do_pixelate(image):
            orig_shape = image.shape
            image_height = orig_shape[0]
            image_width = orig_shape[1]
            dsize = (image_width // pixel_size, image_height // pixel_size)
            image = cv2.resize(image, dsize, interpolation=cv2.INTER_NEAREST)
            dsize = (image_width, image_height)
            image = cv2.resize(image, dsize, interpolation=cv2.INTER_NEAREST)
            return image

        self.operator_on_selection(do_pixelate)

    def operator_gray(self, args):
        """
        ImageProcessor operator_gray method

        This method is responsible for gray scaling operation. using
            opencv cvtColor function.

        """

        def do_gray(image):
            if image.shape == self.image.shape:
                return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            return cv2.cvtColor(gray_image, cv2.COLOR_GRAY2BGR)

        self.operator_on_selection(do_gray)

    def operator_text(self, args):
        """
        ImageProcessor operator_text method

        This method is responsible for text overlay operation. using
            opencv putText function.

        Args:
            args (str): Extra arguments passed to text operator. It
                consist of the following values:
                - text: args[0]
                - scale: args[1]
                - font: args[2]
                - red: args[3]
                - green: args[4]
                - blue: args[5]

        """

        if len(args) < 6:
            return
        center = [self.gravity["x"], self.gravity["y"]]
        if center[0] is None:
            center[0] = self.image_width // 2
        if center[1] is None:
            center[1] = self.image_height // 2
        text = args[0]
        scale = self._safe_float(args[1], 1.0)
        font = self._safe_int(args[2], 0)
        red = self._safe_int(args[3], 255)
        green = self._safe_int(args[4], 255)
        blue = self._safe_int(args[5], 255)
        size = cv2.getTextSize(text, font, scale, 1)
        center[0] -= size[0][0] // 2
        center[1] -= size[1]
        cv2.putText(self.image, text, tuple(center), font, scale, (blue, green, red))

    def operator_object_detection(self, args):
        """
        ImageProcessor operator_text method

        This method is responsible for text overlay operation. using
            opencv putText function.

        Args:
            args (str): Extra arguments passed to text operator. It
                consist of the following values:

        """

        def do_detect(image):
            return self._object_detector.detect_objects(image)

        self.operator_on_selection(do_detect)
