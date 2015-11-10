#!/usr/bin/python

import sys
import getopt

input_file = './input.png'

columns = 104

output_file = './output.png'
scale = 5

threshold = 0.5

text_file = 'text.txt'

font_name = './FreeMono.ttf'
font_size = 12
colorize = False
background = (0, 0, 0, 0)
foreground = (255, 255, 0)

show_output_image = True
also_add_txt = False

verbose = False


def print_help():
    print 'Ascii py: Use a text to render an image.'
    print
    print ' -i <input_image>'
    print ' -o <output_image>'
    print ' -c <columns>'
    print ' -s <scale_of_output_dimensions>'
    print ' -t <threshold_of_white_0_to_1>'
    print ' -T <text_file_to_use>'
    print ' -f <ttf_font_to_use>'
    print ' -S <font_size>'
    print ' -C ... take color from following arguments and not from input image'
    print ' -B <r,g,b_of_background>'
    print ' -F <r,g,b_of_foreground>'
    print ' -a also output as text file'
    print ' -n ... do not show output image'
    print ' -v ... be verbose'
    print
    sys.exit(2)


try:
    opts, args = getopt.getopt(sys.argv[1:], 'hi:o:c:s:t:T:f:CF:B:S:vna')
except getopt.GetoptError as e:
    print 'ERROR: something went wrong: ' + str(e)
    print
    print_help()

for opt, arg in opts:
    if opt == '-h':
        print_help()
    elif opt == '-i':
        input_file = arg
    elif opt == '-o':
        output_file = arg
    elif opt == '-c':
        columns = int(arg)
    elif opt == '-s':
        scale = float(arg)
    elif opt == '-t':
        threshold = float(arg) % 1.0
    elif opt == '-T':
        text_file = arg
    elif opt == '-f':
        font_name = arg
    elif opt == '-C':
        colorize = True
    elif opt == '-B':
        background = tuple(map(int, arg.split(',')))
    elif opt == '-F':
        foreground = tuple(map(int, arg.split(',')))
    elif opt == '-S':
        font_size = int(arg)
    elif opt == '-n':
        show_output_image = False
    elif opt == '-a':
        also_add_txt = True
    elif opt == '-v':
        verbose = True

if verbose:
    print 'input: %s' % input_file
    print 'output: %s' % output_file
    print 'columns: %d' % columns
    print 'scale: %f' % scale
    print 'threshold: %f' % threshold
    print 'text-file: %s' % text_file
    print 'font-name: %s' % font_name
    print 'font-size: %d' % font_size
    print 'colorize: %s' % colorize
    print 'background: %d, %d, %d' % (background[0], background[1], background[2])
    print 'foreground: %d, %d, %d' % (foreground[0], foreground[1], foreground[2])
    print 'show output: %s' % show_output_image
    print 'also output ad text: %s' % also_add_txt
    print 'verbose: True'
    print

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

if verbose:
    print ' ... loading image'

im = Image.open(input_file).convert('RGBA')
width = im.size[0]
height = im.size[1]

if columns >= width:
    print 'ERROR: Column count to big! Please use less then \'%d\' columns ...' % width
    sys.exit(-1)

aspect = float(height) / width
rows = int(columns * aspect)

width_steps = float(width) / columns
height_steps = float(height) / rows

pixels_in_step = width_steps * height_steps

output_width = int(width * scale)
output_height = int(height * scale)

if verbose:
    print 'image \'%s\' (%dx%d = %2.2f) seperated in (%dx%d) = (%d, %d)x steps, each %d wide will be written in \'%s\' with (%d, %d) size' \
          % (input_file, width, height, aspect, columns, rows, width_steps, height_steps, pixels_in_step,
             output_file, output_width, output_height)

if verbose:
    print ' ... loading font'

font = ImageFont.truetype(font_name, font_size)

if verbose:
    print ' ... loading text'

output_image = Image.new("RGBA", (output_width, output_height))

if also_add_txt:
    output_text_file = open(output_file + '.txt', 'w')

text = open(text_file).read()
text_len = len(text)
text_position = 0


def summarize(region):
    summary = (0, 0, 0)

    for x in range(0, region.size[0]):
        for y in range(0, region.size[1]):
            c = region.getpixel((x, y))
            summary = (summary[0] + c[0], summary[1] + c[1], summary[2] + c[2])

    count = (region.size[0] * region.size[1])
    return (summary[0] / count,
            summary[1] / count,
            summary[2] / count)


def put_text(region, color):
    global text
    global text_position
    global text_len
    global font

    draw = ImageDraw.Draw(region)
    text_box = font.getsize(text[text_position % text_len])
    region_box = region.size
    xy = (region_box[0] / 2.0 - text_box[0] / 2.0, region_box[1] / 2.0 - text_box[1] / 2.0)
    draw.text(xy, text[text_position % text_len], fill=color, font=font)

    if also_add_txt:
        output_text_file.write(text[text_position % text_len])

    text_position += 1


def draw_text(x, y, color):
    global output_image
    box_x = int(x * (scale * width_steps))
    box_y = int(y * (scale * height_steps))
    box_width = int(scale * width_steps)
    box_height = int(scale * height_steps)

    box = (box_x, box_y, box_x + box_width, box_y + box_height)
    region = output_image.crop(box)
    region = region.point(lambda p: background)
    put_text(region, color)

    output_image.paste(region, box)


def draw_black(x, y):
    global output_image
    box_x = int(x * (scale * width_steps))
    box_y = int(y * (scale * height_steps))
    box_width = int(scale * width_steps)
    box_height = int(scale * height_steps)

    box = (box_x, box_y, box_x + box_width, box_y + box_height)

    region = output_image.crop(box)
    region = region.point(lambda p: background)

    if also_add_txt:
        output_text_file.write(' ')

    output_image.paste(region, box)


for y in range(0, rows):
    for x in range(0, columns):
        box_x = int(x * width_steps)
        box_y = int(y * height_steps)
        box_width = int(width_steps)
        box_height = int(height_steps)

        box = (box_x, box_y, box_x + box_width, box_y + box_height)
        region = im.crop(box)

        c = summarize(region)
        grey = .2 * c[0] + .5 * c[1] + .3 * c[2]
        if grey > 255 * threshold:
            if colorize:
                draw_text(x, y, foreground)
            else:
                draw_text(x, y, c)
        else:
            draw_black(x, y)

    if verbose:
        print '%.2f%% done ...' % ((float(y) / rows) * 100)

    if also_add_txt:
        output_text_file.write('\n')

if show_output_image:
    output_image.show()

output_image.save(output_file)

if also_add_txt:
    output_text_file.close()
