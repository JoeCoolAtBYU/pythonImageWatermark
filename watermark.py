from PIL import Image, ImageDraw, ImageFont, ImageTk

font_height_multiplier=1.5 # for some reason there are fonts that get cut off using this ensures that they won't get cut off


class FontNotFoundError(Exception):
    pass


def calculate_font_size(image_width, image_height, proportion=0.05):
    """
    Calculate a font size proportional to the image dimensions.

    Parameters:
    - image_width: Width of the image.
    - image_height: Height of the image.
    - proportion: Proportion of the smaller dimension to be used for font size.

    Returns:
    - font_size: Calculated font size.
    """
    return int(min(image_width, image_height) * proportion)


def add_watermark(input_image_path, output_image_path, watermark_text, angle=45, opacity=128, proportion=0.05,
                  font_size=36,
                  font_path=None):
    message = None
    # Open the original image
    original = Image.open(input_image_path).convert("RGBA")
    width, height = original.size

    if font_size is None or font_size <= 100:
        final_font_size = calculate_font_size(width, height, proportion)
    else:
        final_font_size = font_size

    # Create a new transparent image for the watermark
    watermark = Image.new("RGBA", original.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(watermark)

    # Load a font
    if font_path is None:
        font_path = "./fonts/arial.ttf"
    try:
        print(f"font_path: {font_path}")
        font = ImageFont.truetype(font_path, final_font_size)
    except IOError:
        message = f"Font file not found: {font_path} Using default font."
        font = ImageFont.truetype("./fonts/arial.ttf", final_font_size)

    # Calculate the size of the watermark text using textbbox
    text_bbox = draw.textbbox((0, 0), watermark_text, font=font)
    print(f"text_bbox: {text_bbox}")
    text_width = text_bbox[2] - text_bbox[0]
    print(f"text_width: {text_width}")
    text_height = int((text_bbox[3] - text_bbox[1]) * (font_height_multiplier + proportion))
    print(f"text_height: {text_height}")

# todo why is the text getting cut off?
    # Create a single watermark text image
    text_image = Image.new("RGBA", (text_width, text_height), (255, 255, 255, 0))
    text_draw = ImageDraw.Draw(text_image)
    opacity = opacity  # int((opacity_percent / 100) * 255)
    text_draw.text((0, 0), watermark_text, fill=(255, 255, 255, opacity), font=font)

    # Rotate the watermark text image by the specified angle
    rotated_text = text_image.rotate(angle, expand=1)

    # Get the size of the rotated text
    rotated_width, rotated_height = rotated_text.size

    # Tile the watermark across the entire image
    for y in range(0, height, rotated_height):
        for x in range(0, width, rotated_width):
            watermark.paste(rotated_text, (x, y), rotated_text)

    # Combine the original image with the watermark
    watermarked = Image.alpha_composite(original, watermark)

    # Save the result
    watermarked.save(output_image_path, "PNG")
    print(f"Watermarked image saved to {output_image_path}")
    return message

# # Example usage
# imageName = "IMG_2546.JPG"
# input_image_path = "./images/%s" % imageName  # Path to your input image
# output_image_path = f"./images/output/{imageName}-wm100.png"  # Path to save the output image
# watermark_text = "Sample Watermark"  # The watermark text
# angle = 45  # Angle of the watermark
# opacity_percent = 100
# font_size = 200  # Font size of the watermark text
#
# # Optional font path, use a full path if arial.ttf is not found
# font_path = None  # Change to the path of a valid font file if needed
#
# add_watermark(input_image_path, output_image_path, watermark_text, angle, opacity_percent, font_size, font_path)
