from PIL import Image
import numpy as np
import base64
import io
import cv2

# ===== Colored Text =====

def colored_text(text, color_code):
    return f"\033[{color_code}m{text}\033[0m"

def black_text(text):
    return colored_text(text, "30")

def red_text(text):
    return colored_text(text, "31")

def green_text(text):
    return colored_text(text, "32")

def yellow_text(text):
    return colored_text(text, "33")

def blue_text(text):
    return colored_text(text, "34")

def purple_text(text):
    return colored_text(text, "35")

def cyan_text(text):
    return colored_text(text, "36")

def white_text(text):
    return colored_text(text, "37")

# ===== Convert base64 to image =====

def base64_to_image(value, rgb_width, rgb_height):
    if value == "":
        rgb = np.zeros((3, rgb_width, rgb_height))
        return rgb

    img = Image.open(io.BytesIO(base64.b64decode(value)))
    if img.mode != "RGB":
        img = img.convert("RGB")
    
    rgb = np.array(img)
    rgb = np.transpose(rgb, (2, 0, 1))
    return rgb

def get_image_similarity_by_sift(image1, image2) :
    # img1 = cv2.imread(image1, cv2.IMREAD_COLOR)
    # img2 = cv2.imread(image2, cv2.IMREAD_COLOR)
    img1 = np.transpose(image1, (1, 2, 0))
    img2 = np.transpose(image2, (1, 2, 0))
    sift = cv2.SIFT_create()
    keypoints1, descriptors1 = sift.detectAndCompute(img1, None)
    keypoints2, descriptors2 = sift.detectAndCompute(img2, None)
    FLANN_INDEX_KDTREE = 0
    indexParams = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    searchParams = dict(checks=50)
    flann = cv2.FlannBasedMatcher(indexParams, searchParams)
    matches = flann.knnMatch(descriptors1, descriptors2, k=2)
    good_matches = []
    for m, n in matches:
        if m.distance < 0.9 * n.distance:
            good_matches.append(m)
    similarity = len(good_matches) / max(len(keypoints1), len(keypoints2))
    return similarity

def get_image_similarity_by_orb(image1, image2) :
    # img1 = cv2.imread(image1_path, cv2.IMREAD_COLOR)
    # img2 = cv2.imread(image2_path, cv2.IMREAD_COLOR)
    img1 = np.transpose(image1, (1, 2, 0))
    img2 = np.transpose(image2, (1, 2, 0))
    orb = cv2.ORB_create()
    keypoints1, descriptors1 = orb.detectAndCompute(img1, None)
    keypoints2, descriptors2 = orb.detectAndCompute(img2, None)
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(descriptors1, descriptors2)
    matches = sorted(matches, key=lambda x: x.distance)
    similarity = len(matches) / max(len(keypoints1), len(keypoints2))
    return similarity

def get_image_similarity_by_histogram(image1, image2, bins=256):
    # img1 = cv2.imread(image1_path, cv2.IMREAD_COLOR)
    # img2 = cv2.imread(image2_path, cv2.IMREAD_COLOR)
    img1 = np.transpose(image1, (1, 2, 0))
    img2 = np.transpose(image2, (1, 2, 0))
    hist1 = cv2.calcHist([img1], [0], None, [bins], [0, 256])
    hist2 = cv2.calcHist([img2], [0], None, [bins], [0, 256])
    similarity = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
    return similarity
