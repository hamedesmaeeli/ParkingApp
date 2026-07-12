"""
Plate detector based on OpenCV contours.
This detector will be replaced by YOLO in Sprint 2.
"""

import cv2


class PlateDetector:

    def detect(self, frame):
        """
        Detect candidate license plate regions.

        Returns:
            list[(x, y, w, h)]
        """

        candidates = []

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)

        edges = cv2.Canny(gray, 50, 150)

        contours, _ = cv2.findContours(
            edges,
            cv2.RETR_TREE,
            cv2.CHAIN_APPROX_SIMPLE
        )

        for contour in contours:

            area = cv2.contourArea(contour)

            if area < 5000 or area > 80000:
                continue

            peri = cv2.arcLength(contour, True)

            approx = cv2.approxPolyDP(contour, 0.02 * peri, True)

            if len(approx) != 4:
                continue

            x, y, w, h = cv2.boundingRect(contour)

            ratio = w / float(h)

            if 2.8 < ratio < 3.8:
                candidates.append((x, y, w, h))

        return candidates