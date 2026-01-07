#!/bin/python
import os
import subprocess
import platform
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
        "magick -size 1730x350 xc:none -gravity Center -pointsize 80 -fill '#167df0' -font "
        + font
        + ' -annotate 0 "'
        + text
        + '" /tmp/text.png')

def generate_small_tablet_text(text, font):
    print("  " + text.replace("\n", "\\n"))
    os.system(
        "magick -size 1200x550 xc:none -gravity Center -pointsize 80 -fill '#167df0' -font "
        + font
        + ' -annotate 0 "'
        + text
        + '" /tmp/text.png')

def simple_phone(text, background_file, screenshot_file, output_file, font):
    generate_text(text, font)
    os.system('magick templates/' + background_file
              + ' templates/phone.png -geometry +0+0 -composite '
              + screenshot_file + ' -geometry +306+992 -composite '
              + '/tmp/text.png -geometry +0+0 -composite '
              + output_file)
    os.system('mogrify -resize 1120 "' + output_file + '"')


def simple_large_tablet(text, screenshot_file, output_file, font):
    generate_large_tablet_text(text, font)
    os.system('magick ' + screenshot_file + ' -resize 1285 "/tmp/resized-image.png"')
    os.system('magick templates/tablet-10.png '
              + '/tmp/resized-image.png -geometry +224+459 -composite '
              + '/tmp/text.png -geometry +0+0 -composite '
              + output_file)

def simple_small_tablet(text, screenshot_file, output_file, font):
    generate_small_tablet_text(text, font)
    os.system('magick ' + screenshot_file + ' -resize 850 "/tmp/resized-image.png"')
    os.system('magick templates/tablet-7.png '
              + '/tmp/resized-image.png -geometry +170+765 -composite '
              + '/tmp/text.png -geometry +0+0 -composite '
              + output_file)

def two_phones(text, raw_screenshots_path, output_file, font):
    generate_text(text, font)
    os.system('magick templates/background2.png '
              + 'templates/twophones-a.png -geometry +0+10 -composite '
              + raw_screenshots_path + '/03a.png -geometry +119+992 -composite '
              + 'templates/twophones-b.png -geometry +0+0 -composite '
              + raw_screenshots_path + '/03b.png -geometry +479+1540 -composite '
              + '/tmp/text.png -geometry +0+0 -composite '
              + output_file)
    os.system('mogrify -resize 1120 "' + output_file + '"')

def overwrite_if_different(new, original):
    proc = subprocess.Popen(["magick", "compare", "-metric", "PSNR", new, original, "/tmp/difference.png"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = proc.stderr.read().decode(encoding='utf-8')
    if output.find("(0)") != -1:
        os.remove(new)
    else:
        os.replace(new, original)

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

    simple_phone(texts["customize"], 'background2.png', raw_screenshots_path + '/02.png', output_path + '/phone-screenshots/00.new.png', font)
    overwrite_if_different(output_path + '/phone-screenshots/00.new.png', output_path + '/phone-screenshots/00.png')

    simple_phone(texts["subscribe_favorite"], 'background1.png', raw_screenshots_path + '/00.png', output_path + '/phone-screenshots/01.new.png', font)
    overwrite_if_different(output_path + '/phone-screenshots/01.new.png', output_path + '/phone-screenshots/01.png')

    two_phones(texts["theme"], raw_screenshots_path, output_path + '/phone-screenshots/02.new.png', font)
    overwrite_if_different(output_path + '/phone-screenshots/02.new.png', output_path + '/phone-screenshots/02.png')

    simple_phone(texts["playback_speed"], 'background1.png', raw_screenshots_path + '/01.png', output_path + '/phone-screenshots/03.new.png', font)
    overwrite_if_different(output_path + '/phone-screenshots/03.new.png', output_path + '/phone-screenshots/03.png')

    simple_phone(texts["auto_downloads"], 'background2.png', raw_screenshots_path + '/04.png', output_path + '/phone-screenshots/04.new.png', font)
    overwrite_if_different(output_path + '/phone-screenshots/04.new.png', output_path + '/phone-screenshots/04.png')

    simple_phone(texts["discover"], 'background1.png', raw_screenshots_path + '/05.png', output_path + '/phone-screenshots/05.new.png', font)
    overwrite_if_different(output_path + '/phone-screenshots/05.new.png', output_path + '/phone-screenshots/05.png')

    simple_large_tablet(texts["anywhere"], raw_screenshots_path + '/tablet-10-02.png', output_path + '/large-tablet-screenshots/tablet.new.png', font)
    overwrite_if_different(output_path + '/large-tablet-screenshots/tablet.new.png', output_path + '/large-tablet-screenshots/tablet.png')

    simple_small_tablet(texts["subscribe_favorite"], raw_screenshots_path + '/tablet-7-02.png', output_path + '/tablet-screenshots/tablet.new.png', font)
    overwrite_if_different(output_path + '/tablet-screenshots/tablet.new.png', output_path + '/tablet-screenshots/tablet.png')

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
