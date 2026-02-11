#!/bin/python
import os
import subprocess
import platform
import shutil
from pathlib import Path
import json

langs_and_fonts = {
    'ca': 'Sarabun-Bold',
    'de-DE': 'Sarabun-Bold',
    'en-US': 'Sarabun-Bold',
    'fr-FR': 'Sarabun-Bold',
    'he-IL': 'Arimo-Bold',
    'nl-NL': 'Sarabun-Bold',
    'it-IT': 'Sarabun-Bold',
    'es-ES': 'Sarabun-Bold'
    'no-NO': 'Sarabun-Bold'
}


def generate_text(text, font):
    print("  " + text.replace("\n", "\\n"))
    os.system(
        "magick -size 1698x750 xc:none -gravity Center -pointsize 130 -fill '#167df0' -font "
        + font
        + ' -annotate 0 "'
        + text
        + '" /tmp/text.png')


def generate_large_tablet_text(text, font):
    print("  " + text.replace("\n", "\\n"))
    os.system(
        "magick -size 1730x400 xc:none -gravity Center -pointsize 75 -fill '#167df0' -font "
        + font
        + ' -annotate 0 "'
        + text
        + '" /tmp/text.png')


def generate_small_tablet_text(text, font):
    print("  " + text.replace("\n", "\\n"))
    os.system(
        "magick -size 1200x650 xc:none -gravity Center -pointsize 80 -fill '#167df0' -font "
        + font
        + ' -annotate 0 "'
        + text
        + '" /tmp/text.png')


def overwrite_if_different(new, original):
    proc = subprocess.Popen(["magick", "compare", "-metric", "PSNR", new, original, "/tmp/difference.png"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = proc.stderr.read().decode(encoding='utf-8')
    if output.find("(1)") != -1:
        os.remove(new)
    else:
        shutil.move(new, original)


def simple_frame(text, background_file, raw_base_path, screenshot_filename, output_path_base, output_filename, font):
    # Phone
    generate_text(text, font)
    os.system('magick ' + raw_base_path + '/' + screenshot_filename + ' -resize 1080 "/tmp/resized-image.png"')
    os.system('magick templates/phone/' + background_file
              + ' templates/phone/frame.png -geometry +0+0 -composite'
              + ' /tmp/resized-image.png -geometry +306+992 -composite'
              + ' /tmp/text.png -geometry +0+0 -composite'
              + ' /tmp/framed.png')
    os.system('mogrify -resize 1120 "/tmp/framed.png"')
    overwrite_if_different("/tmp/framed.png", output_path_base + '/phone-screenshots/' + output_filename)

    # Small tablet
    generate_small_tablet_text(text, font)
    os.system('magick ' + raw_base_path + '/tablet-7-' + screenshot_filename + ' -resize 855 "/tmp/resized-image.png"')
    os.system('magick templates/tablet-7/' + background_file
              + ' templates/tablet-7/frame.png -geometry +0+0 -composite'
              + ' /tmp/resized-image.png -geometry +168+765 -composite'
              + ' /tmp/text.png -geometry +0+0 -composite'
              + ' /tmp/framed.png')
    overwrite_if_different("/tmp/framed.png", output_path_base + '/tablet-screenshots/' + output_filename)

    # Large tablet
    generate_large_tablet_text(text.replace("\n", " "), font)
    os.system('magick ' + raw_base_path + '/tablet-10-' + screenshot_filename + ' -resize 1294 "/tmp/resized-image.png"')
    os.system('magick templates/tablet-10/' + background_file
              + ' templates/tablet-10/frame.png -geometry +0+0 -composite'
              + ' /tmp/resized-image.png -geometry +215+439 -composite'
              + ' /tmp/text.png -geometry +0+0 -composite'
              + ' /tmp/framed.png')
    overwrite_if_different("/tmp/framed.png", output_path_base + '/large-tablet-screenshots/' + output_filename)


def two_frames(text, raw_base_path, output_path_base, output_filename, font):
    # Phone
    generate_text(text, font)
    os.system('magick ' + raw_base_path + '/03a.png -resize 1080 "/tmp/resized-image-a.png"')
    os.system('magick ' + raw_base_path + '/03b.png -resize 1080 "/tmp/resized-image-b.png"')
    os.system('magick templates/phone/background2.png'
              + ' templates/phone/twoframes-a.png -geometry +0+10 -composite'
              + ' /tmp/resized-image-a.png -geometry +119+992 -composite'
              + ' templates/phone/twoframes-b.png -geometry +0+0 -composite'
              + ' /tmp/resized-image-b.png -geometry +479+1540 -composite'
              + ' /tmp/text.png -geometry +0+0 -composite'
              + ' /tmp/framed.png')
    overwrite_if_different("/tmp/framed.png", output_path_base + '/phone-screenshots/' + output_filename)

    # Small tablet
    generate_small_tablet_text(text, font)
    os.system('magick ' + raw_base_path + '/tablet-7-03a.png -resize 855 "/tmp/resized-image-a.png"')
    os.system('magick ' + raw_base_path + '/tablet-7-03b.png -resize 855 "/tmp/resized-image-b.png"')
    os.system('magick templates/tablet-7/background2.png'
              + ' templates/tablet-7/twoframes-a.png -geometry +0+10 -composite'
              + ' /tmp/resized-image-a.png -geometry +106+765 -composite'
              + ' templates/tablet-7/twoframes-b.png -geometry +0+0 -composite'
              + ' /tmp/resized-image-b.png -geometry +282+1291 -composite'
              + ' /tmp/text.png -geometry +0+0 -composite'
              + ' /tmp/framed.png')
    overwrite_if_different("/tmp/framed.png", output_path_base + '/tablet-screenshots/' + output_filename)

    # Large tablet
    generate_large_tablet_text(text.replace("\n", " "), font)
    os.system('magick ' + raw_base_path + '/tablet-10-03a.png -resize 1294 "/tmp/resized-image-a.png"')
    os.system('magick ' + raw_base_path + '/tablet-10-03b.png -resize 1294 "/tmp/resized-image-b.png"')
    os.system('magick templates/tablet-10/background2.png'
              + ' templates/tablet-10/twoframes-a.png -geometry +0+10 -composite'
              + ' /tmp/resized-image-a.png -geometry +125+439 -composite'
              + ' templates/tablet-10/twoframes-b.png -geometry +0+0 -composite'
              + ' /tmp/resized-image-b.png -geometry +308+702 -composite'
              + ' /tmp/text.png -geometry +0+0 -composite'
              + ' /tmp/framed.png')
    overwrite_if_different("/tmp/framed.png", output_path_base + '/large-tablet-screenshots/' + output_filename)


def generate_screenshots(language, font):
    print(language)
    with open('strings/' + language + '.json') as textDefinitions:
        texts = json.load(textDefinitions)

    raw_screenshots_path = 'raw/' + language
    output_path = '../listings/' + language + "/graphics"
    Path(output_path + '/phone-screenshots').mkdir(parents=True, exist_ok=True)
    Path(output_path + '/tablet-screenshots').mkdir(parents=True, exist_ok=True)
    Path(output_path + '/large-tablet-screenshots').mkdir(parents=True, exist_ok=True)

    if not Path(raw_screenshots_path + '/00.png').is_file():
        raw_screenshots_path = 'raw/en-US'

    simple_frame(texts["customize"], 'background2.png', raw_screenshots_path, '02.png', output_path, '00.png', font)
    simple_frame(texts["subscribe_favorite"], 'background1.png', raw_screenshots_path, '00.png', output_path, '01.png', font)
    two_frames(texts["theme"], raw_screenshots_path, output_path, '02.png', font)
    simple_frame(texts["playback_speed"], 'background1.png', raw_screenshots_path, '01.png', output_path, '03.png', font)
    simple_frame(texts["auto_downloads"], 'background2.png', raw_screenshots_path, '04.png', output_path, '04.png', font)
    simple_frame(texts["discover"], 'background1.png', raw_screenshots_path, '05.png', output_path, '05.png', font)

def check_os():
    """Currently only working on Linux."""
    return platform.system() == 'Linux' or platform.system() == 'Darwin'


def check_packages():
    """ImageMagick and morgify are required."""
    common = b'Version: ImageMagick'
    try:
        return common in subprocess.check_output(['magick', '-version']) and common in subprocess.check_output(
            ['mogrify', '-version'])
    except subprocess.CalledProcessError:
        return False


def check_fonts():
    """Check if required fonts are installed."""
    try:
        for font in langs_and_fonts.values():
            if bytes(font.encode()) not in subprocess.check_output(['fc-list', '-v']):
                return False
    except subprocess.CalledProcessError:
        return False
    return True


if __name__ == '__main__':
    assert (check_os())
    assert (check_packages())
    assert (check_fonts())
    for lang, font in langs_and_fonts.items():
        generate_screenshots(lang, font)
