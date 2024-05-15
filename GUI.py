import glob
import os
import platform
import tkinter as tk
from tkinter import filedialog, messagebox

from PIL import Image, ImageDraw, ImageFont, ImageTk

paddingx = 10
paddingy = 10
font_height_multiplier = 1.5  # for some reason there are fonts that get cut off using this ensures that they won't get cut off
font_dict = {}


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


def add_watermark(image, watermark_text, font_path, font_size, opacity, angle, proportion):
    width, height = image.size

    if font_size is None or font_size <= 100:
        final_font_size = calculate_font_size(width, height, proportion)
    else:
        final_font_size = font_size

    # Load a font
    if font_path is None:
        font_path = "./fonts/arial.ttf"
    try:
        print(f"font_path: {font_path}")
        font_to_use = ImageFont.truetype(font_path, final_font_size)
    except IOError:
        messagebox.showwarning("Font Error", f"Font file not found: {font_path}. Using default font.")
        font_to_use = ImageFont.truetype("./fonts/arial.ttf", final_font_size)

    # Create a new transparent image for the watermark
    watermark = Image.new("RGBA", image.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(watermark)

    try:
        # Calculate the size of the watermark text using textbbox
        text_bbox = draw.textbbox((0, 0), watermark_text, font=font_to_use)
        print(f"text_bbox: {text_bbox}")
        text_width = text_bbox[2] - text_bbox[0]
        print(f"text_width: {text_width}")
        text_height = int((text_bbox[3] - text_bbox[1]) * (font_height_multiplier + proportion))
        print(f"text_height: {text_height}")
    except Exception as e:
        messagebox.showerror("Error calculating size of watermark", str(e))

    # todo why is the text getting cut off?
    # Create a single watermark text image
    text_image = Image.new("RGBA", (text_width, text_height), (255, 255, 255, 0))
    text_draw = ImageDraw.Draw(text_image)
    opacity = opacity  # int((opacity_percent / 100) * 255)
    text_draw.text((0, 0), watermark_text, fill=(255, 255, 255, opacity), font=font_to_use)

    # Rotate the watermark text image by the specified angle
    rotated_text = text_image.rotate(angle, expand=1)

    # Get the size of the rotated text
    rotated_width, rotated_height = rotated_text.size

    # Tile the watermark across the entire image
    for y in range(0, height, rotated_height):
        for x in range(0, width, rotated_width):
            watermark.paste(rotated_text, (x, y), rotated_text)

    # Combine the original image with the watermark and return
    return Image.alpha_composite(image, watermark)


def update_preview():
    print(f"Update Preview")
    input_image_path = input_entry.get()
    watermark_text = watermark_entry.get()
    angle = int(angle_entry.get())
    opacity = int(opacity_entry.get())
    proportion = float(proportion_entry.get())
    font_size = font_size_scale.get()
    selected_fonts = [font_listbox.get(i) for i in font_listbox.curselection()]
    if not input_image_path or not watermark_text or not selected_fonts:
        print("missing some selections")
        print(f"input_image_path {input_image_path}")
        print(f"watermark_text {watermark_text}")
        print(f"selected_fonts {selected_fonts}")
        return
    selected_font = selected_fonts[0]
    try:
        image = Image.open(input_image_path).convert("RGBA")
        image = add_watermark(image, watermark_text, selected_font, font_size, opacity, angle, proportion)
        image.thumbnail((300, 300))
        preview_image = ImageTk.PhotoImage(image)
        preview_label.config(image=preview_image)
        preview_label.image = preview_image
    except Exception as e:
        messagebox.showerror("Error", str(e))


def find_fonts():
    font_dirs = []
    if platform.system() == "Windows":
        font_dirs.append(r"C:\Windows\Fonts")
    elif platform.system() == "Darwin":  # macOS
        font_dirs.extend([
            "/Library/Fonts",
            "/System/Library/Fonts",
            os.path.expanduser("~/Library/Fonts")
        ])
    elif platform.system() == "Linux":
        font_dirs.extend([
            "/usr/share/fonts",
            "/usr/local/share/fonts",
            os.path.expanduser("~/.fonts")
        ])
    font_files = []
    for font_dir in font_dirs:
        for extension in ["*.ttf", "*.otf", "*.ttc"]:
            font_files.extend(glob.glob(os.path.join(font_dir, extension)))
    return font_files


def populate_font_listbox():
    fonts = find_fonts()
    font_dict.clear()
    for font_path in fonts:
        font_name = os.path.splitext(os.path.basename(font_path))[0]
        font_dict[font_name] = font_path
        font_listbox.insert(tk.END, font_name)


def browse_file(entry):
    filename = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")])
    entry.delete(0, tk.END)
    entry.insert(0, filename)


def browse_save_as(entry):
    filename = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
    entry.delete(0, tk.END)
    entry.insert(0, filename)


def on_submit():
    input_image_path = input_entry.get()
    output_image_path = output_entry.get()
    watermark_text = watermark_entry.get()
    angle = int(angle_entry.get())
    opacity = int(opacity_entry.get())
    proportion = float(proportion_entry.get())
    font_size = font_size_scale.get()

    if not selected_font_path.get():
        messagebox.showwarning("Input Error", "Please select a font.")
        return

    if not input_image_path or not output_image_path or not watermark_text:
        messagebox.showwarning("Input Error", "Please fill in all requried fields")
        return

    try:
        original = Image.open(input_image_path).convert("RGBA")
        image = add_watermark(original, watermark_text, selected_font_path.get(), font_size, opacity, angle, proportion)
        image.save(output_image_path, format="PNG")
        messagebox.showinfo("Success", f"Watermarked image saved to {output_image_path}")
    except Exception as e:
        messagebox.showerror("Error", str(e))


def on_font_select(event):
    selected_indices = font_listbox.curselection()
    if selected_indices:
        font_name = font_listbox.get(selected_indices[0])
        selected_font_path.set(font_dict[font_name])
        update_preview()


app = tk.Tk()
app.title("Image Watermarker")

selected_font_path = tk.StringVar()

tk.Label(app, text="Input Image:").grid(row=0, column=0, padx=paddingx, pady=paddingy)
input_entry = tk.Entry(app, width=50)
input_entry.insert(0, "D:/Programming Projects/Python/JoshuaB/100 Days of Python/ImageWatermark/images/IMG_2546.JPG")
input_entry.grid(row=0, column=1, padx=paddingx, pady=paddingy)
tk.Button(app, text="Browse", command=lambda: browse_file(input_entry)).grid(row=0, column=2, padx=paddingx,
                                                                             pady=paddingy)

tk.Label(app, text="Watermark Text:").grid(row=1, column=0, padx=paddingx, pady=paddingy)
watermark_entry = tk.Entry(app, width=50)
watermark_entry.insert(0, "Joshua Barnett")
watermark_entry.grid(row=1, column=1, padx=paddingx, pady=paddingy)

tk.Label(app, text="Output Image:").grid(row=2, column=0, padx=paddingx, pady=paddingy)
output_entry = tk.Entry(app, width=50)
output_entry.grid(row=2, column=1, padx=paddingx, pady=paddingy)
output_entry.insert(0, "D:/Programming Projects/Python/JoshuaB/100 Days of Python/ImageWatermark/images/output/wm9.png")
tk.Button(app, text="Browse", command=lambda: browse_save_as(output_entry)).grid(row=2, column=2, padx=paddingx,
                                                                                 pady=paddingy)

tk.Label(app, text="Angle (degrees):").grid(row=3, column=0, padx=paddingx, pady=paddingy)
angle_entry = tk.Entry(app, width=10)
angle_entry.insert(0, "45")
angle_entry.grid(row=3, column=1, padx=paddingx, pady=paddingy, sticky='w')

tk.Label(app, text="Opacity (0-255):").grid(row=4, column=0, padx=paddingx, pady=paddingy)
opacity_entry = tk.Entry(app, width=10)
opacity_entry.insert(0, "128")
opacity_entry.grid(row=4, column=1, padx=paddingx, pady=paddingy, sticky="w")

tk.Label(app, text="Proportion (0-1):").grid(row=5, column=0, padx=paddingx, pady=paddingy)
proportion_entry = tk.Entry(app, width=10)
proportion_entry.insert(0, "0.05")
proportion_entry.grid(row=5, column=1, padx=paddingx, pady=paddingy, sticky="w")

# Font selection
tk.Label(app, text="Select Font:").grid(row=6, column=0, padx=10, pady=10)

# Create a frame to hold the listbox and scrollbar
font_frame = tk.Frame(app)
font_frame.grid(row=6, column=1, padx=10, pady=10, sticky='w')

# Add a scrollbar to the frame
font_scrollbar = tk.Scrollbar(font_frame)
font_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Add the listbox to the frame
font_listbox = tk.Listbox(font_frame, selectmode=tk.SINGLE, height=6, yscrollcommand=font_scrollbar.set)
font_listbox.pack(side=tk.LEFT, fill=tk.BOTH)

# Configure the scrollbar to work with the listbox
font_scrollbar.config(command=font_listbox.yview)

# Populate the font listbox
populate_font_listbox()

tk.Label(app, text="Font Size:").grid(row=7, column=0, padx=10, pady=10)
font_size_scale = tk.Scale(app, from_=10, to=400, orient=tk.HORIZONTAL)
font_size_scale.set(150)  # default value
font_size_scale.grid(row=7, column=1, padx=10, pady=10, sticky='w')

preview_label = tk.Label(app)
preview_label.grid(row=8, column=0, columnspan=3, pady=paddingy)

tk.Button(app, text="Add Watermark", command=on_submit).grid(row=9, column=0, columnspan=3, pady=20)

watermark_entry.bind("<Tab>", lambda event: update_preview())
watermark_entry.bind("<FocusOut>", lambda event: update_preview())
angle_entry.bind("<Tab>", lambda event: update_preview())
angle_entry.bind("<FocusOut>", lambda event: update_preview())
opacity_entry.bind("<Tab>", lambda event: update_preview())
opacity_entry.bind("<FocusOut>", lambda event: update_preview())
proportion_entry.bind("<Tab>", lambda event: update_preview())
proportion_entry.bind("<FocusOut>", lambda event: update_preview())
font_size_scale.bind("<ButtonRelease-1>", lambda event: update_preview())
font_listbox.bind("<<ListboxSelect>>", on_font_select)

app.mainloop()
