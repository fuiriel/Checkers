def gen_font(size, bold=False):
    font = '-family {Segoe Print} -size %d' % size
    if bold:
        font += ' -weight bold'
    return font
