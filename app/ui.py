import numpy as np
import tkinter as tk
from tkinter import messagebox, simpledialog
from PIL import ImageTk
import matplotlib.pyplot as plt

from app.config import (
    WINDOW_SIZE_DEFAULT,
    K0_DEFAULT,
    K1_DEFAULT,
    K2_DEFAULT,
    K3_DEFAULT,
    WINDOW_TITLE,
    WINDOW_GEOMETRY,
)

from app.image_io import open_image_dialog, save_image_dialog
from app.image_processing import process_color_image_with_alpha, get_luminance_array


def _create_scrollable_canvas(parent, title):
    frame = tk.Frame(parent)
    frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

    tk.Label(frame, text=title).pack()

    canvas = tk.Canvas(frame, bg="gray")

    scroll_x = tk.Scrollbar(frame, orient="horizontal", command=canvas.xview)
    scroll_y = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)

    canvas.configure(
        xscrollcommand=scroll_x.set,
        yscrollcommand=scroll_y.set
    )

    scroll_y.pack(side="right", fill="y")
    scroll_x.pack(side="bottom", fill="x")
    canvas.pack(side="left", fill="both", expand=True)

    return canvas


class AdaptiveContrastApp:
    def __init__(self, root):
        self.root = root
        self.root.title(WINDOW_TITLE)
        self.root.geometry(WINDOW_GEOMETRY)

        self.original_image = None
        self.result_image = None
        self.original_photo = None
        self.result_photo = None

        self.original_luminance = None
        self.result_luminance = None

        self.selected_x = None
        self.selected_y = None

        self._build_ui()

    def _build_ui(self):
        params_frame = tk.Frame(self.root)
        params_frame.pack(pady=5)

        tk.Label(params_frame, text="window_size").grid(row=0, column=0, padx=5)
        self.entry_window_size = tk.Entry(params_frame, width=8)
        self.entry_window_size.grid(row=0, column=1, padx=5)
        self.entry_window_size.insert(0, WINDOW_SIZE_DEFAULT)

        tk.Label(params_frame, text="k0").grid(row=0, column=2, padx=5)
        self.entry_k0 = tk.Entry(params_frame, width=8)
        self.entry_k0.grid(row=0, column=3, padx=5)
        self.entry_k0.insert(0, K0_DEFAULT)

        tk.Label(params_frame, text="k1").grid(row=0, column=4, padx=5)
        self.entry_k1 = tk.Entry(params_frame, width=8)
        self.entry_k1.grid(row=0, column=5, padx=5)
        self.entry_k1.insert(0, K1_DEFAULT)

        tk.Label(params_frame, text="k2").grid(row=0, column=6, padx=5)
        self.entry_k2 = tk.Entry(params_frame, width=8)
        self.entry_k2.grid(row=0, column=7, padx=5)
        self.entry_k2.insert(0, K2_DEFAULT)

        tk.Label(params_frame, text="k3").grid(row=0, column=8, padx=5)
        self.entry_k3 = tk.Entry(params_frame, width=8)
        self.entry_k3.grid(row=0, column=9, padx=5)
        self.entry_k3.insert(0, K3_DEFAULT)

        buttons_frame = tk.Frame(self.root)
        buttons_frame.pack(pady=5)

        tk.Button(
            buttons_frame,
            text="Открыть изображение",
            command=self.open_image
        ).pack(side="left", padx=5)

        tk.Button(
            buttons_frame,
            text="Обработать",
            command=self.process_image
        ).pack(side="left", padx=5)

        tk.Button(
            buttons_frame,
            text="Сохранить результат",
            command=self.save_image
        ).pack(side="left", padx=5)

        tk.Button(
            buttons_frame,
            text="Гистограммы",
            command=self.show_histograms
        ).pack(side="left", padx=5)

        tk.Button(
            buttons_frame,
            text="Разрез по строке",
            command=self.show_row_profile
        ).pack(side="left", padx=5)

        tk.Button(
            buttons_frame,
            text="Разрез по столбцу",
            command=self.show_col_profile
        ).pack(side="left", padx=5)

        self.info_label = tk.Label(self.root, text="Изображение не загружено")
        self.info_label.pack(pady=5)

        self.pixel_info_label = tk.Label(
            self.root,
            text="Пиксель не выбран",
            justify="left",
            anchor="w"
        )
        self.pixel_info_label.pack(fill="x", padx=10, pady=5)

        images_frame = tk.Frame(self.root)
        images_frame.pack(fill="both", expand=True)

        self.canvas_original = _create_scrollable_canvas(
            images_frame,
            "Исходное изображение"
        )

        self.canvas_result = _create_scrollable_canvas(
            images_frame,
            "Результат обработки"
        )

        self.canvas_original.bind(
            "<Button-1>",
            lambda event: self.on_canvas_click(event, self.canvas_original, self.original_image)
        )

        self.canvas_result.bind(
            "<Button-1>",
            lambda event: self.on_canvas_click(event, self.canvas_result, self.result_image)
        )

    def show_image_on_canvas(self, canvas, pil_image, image_type):
        photo = ImageTk.PhotoImage(pil_image)

        canvas.delete("all")
        canvas.create_image(0, 0, anchor="nw", image=photo)
        canvas.config(scrollregion=(0, 0, pil_image.width, pil_image.height))

        if image_type == "original":
            self.original_photo = photo
        else:
            self.result_photo = photo

    def open_image(self):
        try:
            image, file_path = open_image_dialog()
            if image is None:
                return

            self.original_image = image
            self.result_image = None
            self.original_luminance, _, _, _, _ = get_luminance_array(self.original_image)
            self.result_luminance = None
            self.selected_x = None
            self.selected_y = None

            self.show_image_on_canvas(self.canvas_original, self.original_image, "original")
            self.canvas_result.delete("all")
            self.canvas_result.config(scrollregion=(0, 0, 0, 0))

            self.info_label.config(
                text=(
                    f"Загружено: {file_path} | "
                    f"Размер: {self.original_image.width}x{self.original_image.height} | "
                    f"Режим: {self.original_image.mode}"
                )
            )

            self.pixel_info_label.config(text="Пиксель не выбран")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть изображение:\n{e}")

    def process_image(self):
        if self.original_image is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите изображение")
            return

        try:
            window_size = int(self.entry_window_size.get())
            k0 = float(self.entry_k0.get())
            k1 = float(self.entry_k1.get())
            k2 = float(self.entry_k2.get())
            k3 = float(self.entry_k3.get())

            self.result_image = process_color_image_with_alpha(
                self.original_image,
                window_size=window_size,
                k0=k0,
                k1=k1,
                k2=k2,
                k3=k3
            )

            self.result_luminance = get_luminance_array(self.result_image)

            self.show_image_on_canvas(self.canvas_result, self.result_image, "result")

            self.info_label.config(
                text=(
                    "Обработка завершена | "
                    f"Параметры: window_size={window_size}, k0={k0}, "
                    f"k1={k1}, k2={k2}, k3={k3}"
                )
            )

            if self.selected_x is not None and self.selected_y is not None:
                self.update_pixel_info(self.selected_x, self.selected_y)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка обработки:\n{e}")

    def save_image(self):
        if self.result_image is None:
            messagebox.showwarning("Предупреждение", "Нет результата для сохранения")
            return

        try:
            file_path = save_image_dialog(self.result_image)
            if not file_path:
                return

            messagebox.showinfo("Успех", f"Результат сохранён:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить изображение:\n{e}")

    def _canvas_to_image_coords(self, canvas, event):
        x = int(canvas.canvasx(event.x))
        y = int(canvas.canvasy(event.y))
        return x, y

    def on_canvas_click(self, event, canvas, image):
        if image is None:
            return

        x, y = self._canvas_to_image_coords(canvas, event)

        if 0 <= x < image.width and 0 <= y < image.height:
            self.selected_x = x
            self.selected_y = y
            self.update_pixel_info(x, y)

    def update_pixel_info(self, x, y):
        if self.original_luminance is None:
            return

        y_orig = self.original_luminance[y, x]

        text = f"Координаты пикселя: x={x}, y={y} | Яркость исходного: {y_orig:.2f}"

        if self.result_luminance is not None:
            y_res = self.result_luminance[0][y, x]
            text += f" | Яркость обработанного: {y_res:.2f} | Δ={y_res - y_orig:.2f}"
        else:
            text += " | Обработанное изображение ещё не построено"

        self.pixel_info_label.config(text=text)

    def show_histograms(self):
        if self.original_luminance is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите изображение")
            return

        plt.figure()
        plt.hist(self.original_luminance.ravel(), bins=256, range=(0, 255), alpha=0.6, label="Исходное")
        if self.result_luminance is not None:
            plt.hist(self.result_luminance.ravel(), bins=256, range=(0, 255), alpha=0.6, label="Обработанное")

        plt.title("Гистограммы яркости")
        plt.xlabel("Яркость")
        plt.ylabel("Количество пикселей")
        plt.legend()
        plt.grid(True)
        plt.show()

    def show_row_profile(self):
        if self.original_luminance is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите изображение")
            return

        if self.selected_y is not None:
            initial_value = self.selected_y
        else:
            initial_value = 0

        row = simpledialog.askinteger(
            "Разрез по строке",
            f"Введите номер строки [0..{self.original_image.height - 1}]",
            initialvalue=initial_value,
            minvalue=0,
            maxvalue=self.original_image.height - 1
        )
        if row is None:
            return

        x = np.arange(self.original_image.width)

        plt.figure()
        plt.plot(x, self.original_luminance[row, :], label="Исходное")
        if self.result_luminance is not None:
            plt.plot(x, self.result_luminance[row, :], label="Обработанное")

        plt.title(f"Разрез яркости по строке y={row}")
        plt.xlabel("x")
        plt.ylabel("Яркость")
        plt.legend()
        plt.grid(True)
        plt.show()

    def show_col_profile(self):
        if self.original_luminance is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите изображение")
            return

        if self.selected_x is not None:
            initial_value = self.selected_x
        else:
            initial_value = 0

        col = simpledialog.askinteger(
            "Разрез по столбцу",
            f"Введите номер столбца [0..{self.original_image.width - 1}]",
            initialvalue=initial_value,
            minvalue=0,
            maxvalue=self.original_image.width - 1
        )
        if col is None:
            return

        y = np.arange(self.original_image.height)

        plt.figure()
        plt.plot(y, self.original_luminance[:, col], label="Исходное")
        if self.result_luminance is not None:
            plt.plot(y, self.result_luminance[:, col], label="Обработанное")

        plt.title(f"Разрез яркости по столбцу x={col}")
        plt.xlabel("y")
        plt.ylabel("Яркость")
        plt.legend()
        plt.grid(True)
        plt.show()