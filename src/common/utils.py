def gen_font(size, bold=False):
    font = '-family {Segoe Print} -size %d' % size
    if bold:
        font += ' -weight bold'
    return font


def calc_dimensions(row, column, width, height, border):
    y1 = (row * width) + border
    y2 = ((row + 1) * width) - border
    x1 = (column * height) + border
    x2 = ((column + 1) * height) - border
    return x1, y1, x2, y2
