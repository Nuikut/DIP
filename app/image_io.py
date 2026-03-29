from PIL import Image
from tkinter import filedialog


def open_image_dialog():
    file_path = filedialog.askopenfilename(
        title="Выберите изображение",
        filetypes=[
            ("Image files", "*.bmp *.png *.jpg *.jpeg"),
            ("All files", "*.*")
        ]
    )

    if not file_path:
        return None, None

    image = Image.open(file_path)
    return image, file_path


def save_image_dialog(image):
    file_path = filedialog.asksaveasfilename(
        title="Сохранить результат",
        defaultextension=".bmp",
        filetypes=[
            ("BMP files", "*.bmp"),
            ("PNG files", "*.png"),
            ("JPEG files", "*.jpg"),
            ("All files", "*.*")
        ]
    )

    if not file_path:
        return None

    image.save(file_path)
    return file_path