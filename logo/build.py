from os import listdir, mkdir, getenv
from shutil import rmtree
from os.path import exists, dirname, realpath
from wand.image import Image
from wand.color import Color
import xml.etree.ElementTree as ET

skip_icons = getenv('SKIP_ICONS') == 'true'

out_sizes = [ 8, 16, 32, 64, 128, 256, 512, 1024 ]

icon_colors = [ 'black', 'primary', 'white' ]
text_colors = [ 'black', 'white' ]
bg_colors = [ 'none', 'white', 'black', 'primary' ]

script_dir = dirname(realpath(__file__))


def generate_svg_logo(icon_color, text_color, output_path):
    """Generate a combined SVG logo from icon and text SVG files."""
    # Read and parse the icon SVG
    icon_tree = ET.parse(f'{script_dir}/src/icon-{icon_color}.svg')
    icon_root = icon_tree.getroot()

    # Read and parse the text SVG
    text_tree = ET.parse(f'{script_dir}/src/text-{text_color}.svg')
    text_root = text_tree.getroot()

    # Get viewBox from icon (this is the coordinate space we need to scale from)
    icon_viewbox = icon_root.get('viewBox', '0 0 192 192')
    icon_vb_parts = icon_viewbox.split()
    icon_vb_width = float(icon_vb_parts[2])
    icon_vb_height = float(icon_vb_parts[3])

    # Get dimensions from text SVG
    text_viewbox = text_root.get('viewBox', '0 0 16800.396 2903.0359')
    text_vb_parts = text_viewbox.split()
    text_vb_width = float(text_vb_parts[2])
    text_vb_height = float(text_vb_parts[3])

    # Match PNG dimensions: icon is 4096x4096, text uses its natural dimensions
    icon_pixel_size = 4096
    scale_factor = icon_pixel_size / icon_vb_width  # Scale from viewBox to pixel size

    # Match PNG positioning: text at (icon_width + 1260, 872)
    spacing = 1260
    text_x = icon_pixel_size + spacing  # 5356
    text_y = 872

    # Canvas dimensions match PNG: width = icon + spacing + text, height = icon height
    total_width = icon_pixel_size + spacing + text_vb_width
    total_height = icon_pixel_size

    # Create new SVG root
    svg_ns = 'http://www.w3.org/2000/svg'
    ET.register_namespace('', svg_ns)

    new_svg = ET.Element('{%s}svg' % svg_ns, {
        'width': str(total_width),
        'height': str(total_height),
        'viewBox': f'0 0 {total_width} {total_height}'
    })

    # Create a group for the icon, scale from viewBox (192x192) to pixel size (4096x4096)
    icon_group = ET.SubElement(new_svg, 'g', {
        'transform': f'scale({scale_factor})'
    })

    # Copy icon paths to the icon group
    for child in icon_root:
        if child.tag.endswith('path'):
            icon_group.append(child)

    # Create a group for the text at the PNG position (5356, 872)
    text_group = ET.SubElement(new_svg, 'g', {
        'transform': f'translate({text_x}, {text_y})'
    })

    # Copy text paths to the text group
    for child in text_root:
        if child.tag.endswith('path'):
            text_group.append(child)

    # Write the combined SVG to file
    tree = ET.ElementTree(new_svg)
    ET.indent(tree, space='  ')
    tree.write(output_path, encoding='utf-8', xml_declaration=True)


if not exists(f'{script_dir}/out'):
    mkdir(f'{script_dir}/out')
else:
    rmtree(f'{script_dir}/out')
    mkdir(f'{script_dir}/out')


for icolor in icon_colors:
    with Image(filename=f'{script_dir}/src/icon-{icolor}.svg', background=Color('transparent')) as image:
        backgrounds = ['transparent', 'white', 'black', 'primary']
        backgrounds = filter(lambda color: icolor != color, backgrounds)

        for bgcolor in backgrounds:
            bgcolor_code = bgcolor
            if icolor == "black" and bgcolor_code == "primary":
                continue
            if bgcolor_code == "primary":
                bgcolor_code = "#10B981"
            with Image(width=image.width + 1024, height=image.height + 1024,
                background=Color(bgcolor_code)) as bg:
                bg.composite(image, 512, 512)
                for size in out_sizes:
                    with Image.convert(bg, 'png') as out:
                        out.resize(size, size)
                        out.save(filename=f'{script_dir}/out/icon-bg_{bgcolor}-{icolor}-{size}x.png')
            for size in out_sizes:
                with Image.convert(image, 'png') as out:
                    out.resize(size, size)
                    out.save(filename=f'{script_dir}/out/icon-{icolor}-{size}x.png')
        
        for tcolor in text_colors:
            if (icolor == "white" and tcolor == "black") or (icolor == "black" and tcolor == "white"):
                continue
            with Image(filename=f'{script_dir}/src/text-{tcolor}.svg', background=Color('transparent')) as text:
                backgrounds = [ 'transparent', 'white', 'black', 'primary' ]
                backgrounds = filter(lambda color: icolor != color, backgrounds)
                backgrounds = filter(lambda color: tcolor != color, backgrounds)

                for bgcolor in list(backgrounds):
                    bgcolor_code = bgcolor
                    if (icolor == "black" or tcolor == "black") and bgcolor_code == "primary":
                        continue
                    elif bgcolor_code == "primary":
                        bgcolor_code = "#10B981"
                    with Image(width=image.width + 512 + 1260 + text.width + 512, height=image.height + 1024,
                        background=Color(bgcolor_code)) as bg:
                        bg.composite(image, 512, 512)
                        bg.composite(text, 5868, 1384)
                        for size in out_sizes:
                            with Image.convert(bg, 'png') as out:
                                out_scale = bg.height / size
                                out.resize(height=size, width=int(bg.width / out_scale))
                                out.save(filename=f'{script_dir}/out/logo-padded-bg_{bgcolor}-{icolor}_{tcolor}-{size}x.png')
                    with Image(width=image.width + 1260 + text.width, height=image.height,
                        background=Color(bgcolor_code)) as bg:
                        bg.composite(image, 0, 0)
                        bg.composite(text, 5356, 872)
                        for size in out_sizes:
                            with Image.convert(bg, 'png') as out:
                                out_scale = bg.height / size
                                out.resize(height=size, width=int(bg.width / out_scale))
                                out.save(filename=f'{script_dir}/out/logo-bg_{bgcolor}-{icolor}_{tcolor}-{size}x.png')

# Generate SVG logo variants
svg_variants = [
    ('white', 'white', 'logo-white_white.svg'),
    ('black', 'black', 'logo-black_black.svg'),
    ('primary', 'black', 'logo-primary_black.svg'),
    ('primary', 'white', 'logo-primary_white.svg')
]

for icon_color, text_color, filename in svg_variants:
    output_path = f'{script_dir}/out/{filename}'
    generate_svg_logo(icon_color, text_color, output_path)
    print(f'Generated: {filename}')
