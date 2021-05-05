from os import listdir, mkdir, getenv
from shutil import rmtree
from os.path import exists, dirname, realpath
from wand.image import Image
from wand.color import Color

skip_icons = getenv('SKIP_ICONS') == 'true'

out_sizes = [ 8, 16, 32, 64, 128, 256, 512, 1024 ]

icon_colors = [ 'black', 'primary', 'white' ]
text_colors = [ 'black', 'white' ]
bg_colors = [ 'none', 'white', 'black', 'primary' ]

script_dir = dirname(realpath(__file__))


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
