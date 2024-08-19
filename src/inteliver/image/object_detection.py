from typing import Any

import cv2
import numpy as np
from ultralytics import YOLO


class ObjectDetection:
    _model = None  # Class variable to store the model
    _colors = np.random.randint(0, 255, size=(100, 3))

    def __init__(self, model_path: str = "src/inteliver/assets/models/yolo/yolov8n.pt"):
        """
        Initialize the ObjectDetection class with the YOLOv8 model.
        Load the model only once if not already loaded.

        Args:
            model_path (str): The file path to the pre-trained YOLOv8 model.
        """
        if ObjectDetection._model is None:
            ObjectDetection._model = self._load_model(model_path)

    def _load_model(self, model_path: str) -> YOLO:
        """
        Load the YOLOv8 model from the given path.

        Args:
            model_path (str): The file path to the pre-trained YOLOv8 model.

        Returns:
            YOLO: The YOLOv8 model.
        """
        return YOLO(model_path)

    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess the image for the model.

        Args:
            image (np.ndarray): The input image as a numpy array.

        Returns:
            np.ndarray: The preprocessed image.
        """
        # Convert image to RGB
        if image.shape[2] == 4:  # Handle transparency channel
            image = cv2.cvtColor(image, cv2.COLOR_BGRA2RGB)
        else:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return image

    def _postprocess_detections(
        self, results
    ) -> list[tuple[int, int, int, int, str, float]]:
        """
        Post-process the detections to extract bounding boxes and labels.

        Args:
            results: The detections from the model.

        Returns:
            List[Tuple[int, int, int, int, str]]: List of detected objects as (x1, y1, x2, y2, label).
        """
        detections = []
        for result in results:
            boxes = result.boxes.xyxy.cpu().numpy()  # Bounding boxes
            labels = result.boxes.cls.cpu().numpy().astype(int)  # Class labels
            confidences = result.boxes.conf.cpu().numpy()  # Confidences

            # Get class names from the COCO dataset
            class_names = result.names

            for box, label, confidence in zip(boxes, labels, confidences):
                detections.append((*box, class_names[label], confidence))

        return detections

    def _draw_boxes(
        self, image: np.ndarray, detections: list[tuple[int, int, int, int, str, float]]
    ) -> np.ndarray:
        """
        Draw bounding boxes and labels on the image.

        Args:
            image (np.ndarray): The input image as a numpy array.
            detections (List[Tuple[int, int, int, int, str]]): The detected objects.

        Returns:
            np.ndarray: The image with bounding boxes and labels drawn.
        """
        for x1, y1, x2, y2, label, confidence in detections:
            # Get color for the label
            color = ObjectDetection._colors[hash(label) % len(ObjectDetection._colors)]
            # Convert to tuple format
            color = (
                int(color[0]),
                int(color[1]),
                int(color[2]),
            )
            cv2.rectangle(image, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
            cv2.putText(
                image,
                f"{label}-{confidence:.2f}",
                (int(x1), int(y1) - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                color,
                2,
            )

        return image

    def detect_objects(self, image: np.ndarray) -> np.ndarray:
        """
        Detect objects in the image and draw bounding boxes with labels.

        Args:
            image (np.ndarray): The input image as a numpy array.

        Returns:
            np.ndarray: The image with detected objects drawn.
        """
        # Detect objects
        detections = self._detect(image)

        # Draw bounding boxes
        image_with_boxes = self._draw_boxes(image, detections)

        return image_with_boxes

    def detect_objects_map(self, image: np.ndarray) -> dict[str, list[dict[str, Any]]]:
        """
        Detect objects in the image and return an object map.

        Args:
            image (np.ndarray): The input image as a numpy array.

        Returns:
            Dict[str, List[Dict[str, Any]]]: The object map with detected objects' names, coordinates, and confidence.
        """
        # Detect objects
        detections = self._detect(image)

        # Build object map
        object_map: dict = {}
        for x1, y1, x2, y2, label, confidence in detections:
            if label not in object_map:
                object_map[label] = []
            object_map[label].append(
                {
                    "x1": int(x1),
                    "y1": int(y1),
                    "x2": int(x2),
                    "y2": int(y2),
                    "confidence": float(confidence),
                }
            )

        return object_map

    def _detect(self, image: np.ndarray) -> list[tuple[int, int, int, int, str, float]]:
        """
        Detect objects in the image.

        Args:
            image (np.ndarray): The input image as a numpy array.

        Returns:
            np.ndarray: The image with detected objects drawn.
        """
        # Preprocess the image
        preprocessed_image = self._preprocess_image(image)

        # Perform detection
        results = self._model(preprocessed_image)

        # Post-process detections
        detections = self._postprocess_detections(results)

        return detections
