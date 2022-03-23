import struct
import typing

import matplotlib.pyplot as plt
from osgeo import gdal

from ds import band, IMAGE_WIDTH, IMAGE_HEIGHT

CrossSection = list[tuple[float, float]]


def read_horizontal_scanline(x_offset: int, y_offset: int, width: int) -> tuple[float]:
    try:
        scanline = band.ReadRaster(
            xoff=x_offset,
            yoff=y_offset,
            xsize=width,
            ysize=1,
            buf_xsize=width,
            buf_ysize=1,
            buf_type=gdal.GDT_Float32
        )
    except RuntimeError:
        print("Caught RuntimeError while reading scanline:")
        print("x_offset", x_offset)
        print("y_offset", y_offset)
        print("width", width)
        raise

    return typing.cast(tuple[float], struct.unpack('f' * width, scanline))


def get_scanlines_to_read(start_x: int, end_x: int, start_y: int, end_y: int) -> list[tuple[int, tuple[int, int]]]:
    slope = (end_x - start_x) / (end_y - start_y + 1)  # For every y, how many x's do we change
    x_size = round(slope) + 1

    result = []

    for y in range(start_y, end_y + 1):
        first_x = round(slope * (y - start_y)) + start_x
        last_x = first_x + x_size

        result.append((y, (first_x, last_x)))

    return result


def read_line(start_x: int, start_y: int, end_x: int, end_y: int) -> list[float]:
    lines = get_scanlines_to_read(start_x, end_x, start_y, end_y)

    result = []

    for line in lines:
        y = line[0]
        x = line[1]
        result += read_horizontal_scanline(x[0], y, x[1] - x[0])

    return result


def normalize(line: list[float]) -> CrossSection:
    length = len(line)

    min_height = min(line)
    max_height = max(line)

    height_diff = max_height - min_height

    return [(i/length, (line[i] - min_height) / height_diff) for i in range(length)]


def coord_to_x_y(lat: float, long: float) -> tuple[int, int]:
    """
    :param lat: -90 to 90
    :param long: -180 to 180
    :return: x, y pixel coordinates from the tiff image
    """
    x = ((long + 180) / 360) * IMAGE_WIDTH
    y = ((-lat + 90) / 180) * IMAGE_HEIGHT

    return round(x), round(y)


def generate_normalized_cross_sections(feature: dict) -> tuple[CrossSection, CrossSection]:
    start_x, start_y = coord_to_x_y(float(feature["northernLatitude"]), float(feature["westernLongitude"]))
    end_x, end_y = coord_to_x_y(float(feature["southernLatitude"]), float(feature["easternLongitude"]))

    horizontal_midpoint = round((start_x + end_x) / 2)
    vertical_midpoint = round((start_y + end_y) / 2)

    try:
        horizontal_cs = normalize(read_line(start_x, vertical_midpoint, end_x, vertical_midpoint))
        vertical_cs = normalize(read_line(horizontal_midpoint, start_y, horizontal_midpoint, end_y))
    except RuntimeError:
        print("Runtime error generated while trying to read line for", feature["name"])
        raise

    return horizontal_cs, vertical_cs


def plot_cross_section(cross_section: CrossSection):
    xs, ys = zip(*cross_section)

    plt.plot(xs, ys)
    plt.show()


def get_y_value(line: CrossSection, x: float) -> float:
    xs, ys = zip(*line)

    indx = None

    for i, x_ in enumerate(xs):
        if x_ >= x:
            indx = i
            break

    if indx is None:
        indx = len(line) - 1

    # if indx is None:
    #     raise ValueError("Invalid x value provided. Should be between 0 and 1.")

    if len(line) - 1 == indx:
        return ys[indx]

    next_indx = indx + 1

    return (ys[indx] + ys[next_indx]) / 2
