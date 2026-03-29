import numpy as np
from PIL import Image


def local_mean_std(img, window_size):
    if window_size < 1:
        raise ValueError("window_size должен быть >= 1")

    pad_before = window_size // 2
    pad_after = window_size - pad_before - 1

    padded = np.pad(
        img,
        ((pad_before, pad_after), (pad_before, pad_after)),
        mode='reflect'
    )

    h, w = img.shape
    mu = np.zeros((h, w), dtype=np.float32)
    sigma = np.zeros((h, w), dtype=np.float32)

    for i in range(h):
        for j in range(w):
            window = padded[i:i + window_size, j:j + window_size]

            mu[i, j] = np.mean(window)
            sigma[i, j] = np.std(window)

    return mu, sigma


def adaptive_contrast_gray(img, window_size=7, k0=2.0, k1=0.5, k2=0.02, k3=0.4):
    img = img.astype(np.float32)

    mu_global = np.mean(img)
    sigma_global = np.std(img)

    mu_local, sigma_local = local_mean_std(img, window_size)

    result = img.copy()

    mask = (
        (mu_local <= k1 * mu_global) &
        (sigma_local >= k2 * sigma_global) &
        (sigma_local <= k3 * sigma_global)
    )

    result[mask] = k0 * result[mask]

    return np.clip(result, 0, 255).astype(np.uint8)


def process_color_image_with_alpha(img_pil, window_size=7, k0=2.0, k1=0.5, k2=0.02, k3=0.4):
    img = img_pil.convert("RGBA")
    img_np = np.array(img).astype(np.float32)

    # разделяем
    r = img_np[:, :, 0]
    g = img_np[:, :, 1]
    b = img_np[:, :, 2]
    a = img_np[:, :, 3]  # альфа сохраняем

    # яркость
    y = 0.299 * r + 0.587 * g + 0.114 * b
    y_uint8 = np.clip(y, 0, 255).astype(np.uint8)

    y_processed = adaptive_contrast_gray(
        y_uint8,
        window_size=window_size,
        k0=k0,
        k1=k1,
        k2=k2,
        k3=k3
    ).astype(np.float32)

    ratio = y_processed / (y + 1e-5)

    r_new = np.clip(r * ratio, 0, 255)
    g_new = np.clip(g * ratio, 0, 255)
    b_new = np.clip(b * ratio, 0, 255)

    result = np.stack((r_new, g_new, b_new, a), axis=2).astype(np.uint8)

    return Image.fromarray(result, mode="RGBA")


if __name__ == "__main__":
    input_path = "input.bmp"
    output_path = "output.bmp"

    img = Image.open(input_path)

    print("Режим входного изображения:", img.mode)

    result_img = process_color_image_with_alpha(
        img,
        window_size=7,
        k0=2.0,
        k1=0.5,
        k2=0.02,
        k3=0.4
    )

    result_img.save(output_path)

    print("Обработка завершена.")
    print("Результат сохранён в", output_path)