from ..utils import purple_text
from ..utils import get_image_similarity_by_sift, get_image_similarity_by_orb, get_image_similarity_by_histogram
std_print = print
def print(*args, end='\n'):
    text = [purple_text(str(arg)) for arg in args]
    std_print("[Tasks]", *text, end=end)