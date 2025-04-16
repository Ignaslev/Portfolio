from PIL import Image
from django.conf import settings
import os


from io import BytesIO
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

def generate_burger_image(ingredient_images, burger_id, top_bun_image):
    '''
    Generates a custom burger image and saves it to S3 (or current storage backend).
    '''
    # GET BOTTOM BUN
    bottom_bun_path = os.path.join(settings.MEDIA_ROOT, 'burger_components/bottom-bun.png')
    bottom_bun = Image.open(bottom_bun_path)

    # GET TOP BUN
    top_bun_path = os.path.join(settings.MEDIA_ROOT, top_bun_image)
    top_bun = Image.open(top_bun_path)

    # GET REST OF INGREDIENTS
    middle_images = [Image.open(os.path.join(settings.MEDIA_ROOT, img_path)) for img_path in ingredient_images]

    # COMBINE ALL INGREDIENTS
    all_images = [top_bun] + middle_images + [bottom_bun]

    # SET TOTAL HEIGHT ( SUM OF ALL INGREDIENTS IMAGES HEIGHTS) AND WIDTH
    total_height = sum(img.height for img in all_images)
    max_width = 300

    final_image = Image.new('RGBA', (max_width, total_height), (255, 255, 255, 0))

    y_offset = 0
    for img in all_images:
        final_image.paste(img, (0, y_offset), img)
        y_offset += img.height - 20

    # Save to memory instead of file system
    buffer = BytesIO()
    final_image.save(buffer, format='PNG')
    buffer.seek(0)

    image_name = f'custom_burgers/custom-burger-id-{burger_id}.png'

    # Save using Django's storage (S3 in your case)
    default_storage.save(image_name, ContentFile(buffer.read()))

    return image_name

