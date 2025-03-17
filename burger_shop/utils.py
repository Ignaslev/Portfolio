from PIL import Image
from django.conf import settings
import os


def generate_burger_image(ingredient_images, burger_id, top_bun_image):
    '''
    Generates a custom burger image by stacking ingredient images.

    Parameters:
    - ingredient_images: List of ingredient image paths (excluding buns).
    - burger_id : ID of the CustomBurger(for naming the output image).
    - top_bun_image: Path to the top bun image.

    Process:
    - Opens the bottom bun, top bun, and ingredient images.
    - Stacks them vertically with a small overlap.
    - Saves the final image in the 'custom_burgers' folder.

    Returns:
    - str of generated image path
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

    # PILLOW CREATES EMPTY IMAGE TO BUILD ON
    final_image = Image.new('RGBA', (max_width, total_height), (255, 255, 255, 0))

    # PASTES IMAGES ON BLANK IMAGE ON TOP OF EACHOTHER
    y_offset = 0
    for img in all_images:
        final_image.paste(img, (0, y_offset), img)
        y_offset += img.height - 20

    # SETTING FOLDER WHERE TO SAVE
    final_folder = os.path.join(settings.MEDIA_ROOT, 'custom_burgers')
    os.makedirs(final_folder, exist_ok=True)

    # SAVES FINAL IMAGE WITH CUSTOM NAME( EACH IMAGE HAS ITS CUSTOM BURGER ID)
    final_path = os.path.join(final_folder, f'custom-burger-id-{burger_id}.png')
    final_image.save(final_path)

    # RETURN COMPLETE IMAGE PATH TO VIEW TO ASSIGN TO CUSTOM BURGER IN DATABASE
    return f'custom_burgers/custom-burger-id-{burger_id}.png'
