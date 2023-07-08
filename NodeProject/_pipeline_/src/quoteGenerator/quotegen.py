import os, random, sys
base_dir = os.path.dirname(os.path.abspath(__file__))
'''
src_dir = os.sep.join(base_dir.split(os.sep)[:-1])
site_package_dir = src_dir + os.sep + 'site-packages'
if not site_package_dir in sys.path:
    sys.path.insert(0, site_package_dir)
'''
from PIL import Image, ImageDraw, ImageFont


element_dir = base_dir + os.sep + 'elements'
font_dir = base_dir + os.sep + 'fonts'

class imgen:
    @staticmethod # PIL Version 5
    def render_text_legacy(text, font_path, text_color, bg_color, img_width, img_height, bg_alpha, line_spacing, al='center',
                    save_path=None, max_size=120, shadow_offset=7, border_pecentile=0.025):
        text_split = text.split('\n')
        text_split = [i + '\n' for i in text_split if not i == '']
        text = ''.join(text_split)
        if text[0] == ' ': text = text[0:]
        if text[-1] == '\n': text = text[:-1]

        # Create image with alpha channel
        img = Image.new("RGBA", (img_width, img_height), (0, 0, 0, 0))

        # Draw text on image
        draw = ImageDraw.Draw(img)
        font_size = 0
        font = ImageFont.truetype(font_path, font_size)
        for i in range(max_size):
            text_width, text_height = draw.textsize(text, font=font, spacing=line_spacing)
            if text_width > (img_width - (img_width * border_pecentile)) or text_height > (
                    img_height - (img_height * border_pecentile)):
                break
            else:
                font_size += 1
                font = ImageFont.truetype(font_path, font_size)

        # Calculate the position to align the text
        if al == 'left':
            pos_x = 0
        elif al == 'right':
            pos_x = img_width - text_width
        else:  # Center alignment
            pos_x = (img_width - text_width) // 2
        pos_y = (img_height - text_height) // 2

        if shadow_offset != 0:
            draw.text((pos_x + shadow_offset, pos_y + shadow_offset), text, font=font, fill=(0, 0, 0, 70),
                      align=al)
        draw.text((pos_x, pos_y), text, font=font, fill=text_color, align=al)

        # Apply background color and alpha
        if bg_alpha < 255:
            bg_color += (int(bg_alpha),)
        bg = Image.new("RGBA", img.size, bg_color)
        img = Image.alpha_composite(bg, img)

        # Save image
        if save_path:
            img.save(save_path, format='png')
        return img

    @staticmethod
    def render_text(text, font_path, text_color, bg_color, img_width, img_height, bg_alpha, line_spacing, al='center', save_path=None, max_size=120, shadow_offset=7, border_pecentile=0.025):
        text_split = text.split('\n')
        text_split = [i+'\n' for i in text_split if not i == '']
        text = ''.join(text_split)
        if text[0] == ' ': text = text[0:];
        if text[-1] == '\n': text = text[:-1];

        # Create image with alpha channel
        img = Image.new("RGBA", (img_width, img_height), (0, 0, 0, 0))

        # Init orig position
        pos_x, pos_y = (img_width / 2, img_height / 2)

        # Draw text on image
        draw = ImageDraw.Draw(img)
        font_size = 0
        font = ImageFont.truetype(font_path, font_size)
        for i in range(max_size):
            tb = draw.textbbox((pos_x,pos_y), text, font, 'mm', line_spacing, al, embedded_color=text_color) #lf, tp, rg, bt
            if tb[2] > (img_width-(img_width*border_pecentile)) or tb[3] > (img_height-(img_height*border_pecentile)):
                break
            else:
                font_size += 1
                font = ImageFont.truetype(font_path, font_size)
        #print(tb, img_width, img_height)
        #print(font_size)

        # Offset position
        if al == 'center':
            pos_x, pos_y = (img_width / 2, img_height / 2)
        elif al == 'left':
            pos_x -= abs((img_width * border_pecentile) - tb[0])
        elif al == 'right':
            pos_x += abs((img_width * border_pecentile) - tb[0])

        if shadow_offset != 0:
            draw.text((pos_x+shadow_offset, pos_y+shadow_offset), text, font=font, fill=(0,0,0,70), align=al, anchor='mm', spacing=line_spacing)
        draw.text((pos_x,pos_y), text, font=font, fill=text_color, align=al, anchor='mm', spacing=line_spacing)

        # Apply background color and alpha
        if bg_alpha < 255:
            bg_color += (int(bg_alpha),)
        img = img.rotate(0, expand=True)
        bg = Image.new("RGBA", img.size, bg_color)
        img = Image.alpha_composite(bg, img)

        # Save image
        if save_path:
            img.save(save_path, format='png')
        #print(al)
        return img

    @staticmethod
    def get_bg_path():
        bg_dir = element_dir + '/bg'
        bg_path_ls = [(bg_dir + os.sep + i).replace('\\','/') for i in os.listdir(bg_dir)]
        #print(bg_path_ls)
        return bg_path_ls[random.randint(0, len(bg_path_ls)-1)]

    @staticmethod
    def get_logo_path():
        logo_dir = element_dir + '/logo'
        logo_path_ls = [(logo_dir + os.sep + i).replace('\\', '/') for i in os.listdir(logo_dir)]
        #print(logo_path_ls)
        return logo_path_ls[random.randint(0, len(logo_path_ls)-1)]

    @staticmethod
    def get_qr_path():
        return element_dir + '/qr_link.png'

    @staticmethod
    def create_quote_image():
        bg = Image.open(imgen.get_bg_path())

        def load_image(img_path, size=None, scale=[1.0,1.0]):
            img = Image.open(img_path)
            if size:
                img = img.resize((int(size[0]), int(size[1])))
            else:
                img = img.resize((int(img.width / scale[0]), int(img.width / scale[1])))
            img = img.convert('RGBA')
            alpha_mask = img.getchannel('A')
            return [img, alpha_mask]

        logo = load_image(imgen.get_logo_path(), size=[415,415])
        logo_x = int((bg.width - logo[0].width) - 129)
        logo_y = int((bg.height - logo[0].height) - 58)
        bg.paste(logo[0], (logo_x, logo_y), logo[1])

        qr = load_image(imgen.get_qr_path(), size=[415,415])
        qr_x = int(128)
        qr_y = int((bg.height - qr[0].height) - 58)
        bg.paste(qr[0], (qr_x, qr_y), qr[1])

        tx_head = load_image(element_dir + '/text_head.png', size=[1702,131])
        tx_head_x = int((bg.width - tx_head[0].width)*.5)
        tx_head_y = int(197)
        bg.paste(tx_head[0], (tx_head_x, tx_head_y), tx_head[1])

        tx_con = load_image(element_dir + '/text_content.png', size=[1709, 729])
        tx_con_x = int((bg.width - tx_con[0].width) * .5)
        tx_con_y = int(441)
        bg.paste(tx_con[0], (tx_con_x, tx_con_y), tx_con[1])

        tx_cred = load_image(element_dir + '/text_credit.png', size=[1702, 131])
        tx_cred_x = int((bg.width - tx_con[0].width) * .5)
        tx_cred_y = int(1237)
        bg.paste(tx_cred[0], (tx_cred_x, tx_cred_y), tx_cred[1])

        # Save the new image to disk
        out_path = base_dir + '/output/quote_img.png'
        bg.save(out_path)
        return out_path

def run(head_text='head', content_text='content', credit_text='credit'):
    render_text_rec = [
        {
            'text_type': 'head',
            'text': head_text,
            'font_path': font_dir + '/FC Minimal Regular.otf',
            'text_color': (255, 255, 255),
            'bg_color': (0, 0, 0),
            'img_width': 1702,
            'img_height': 131,
            'bg_alpha': 0,  # 0-255
            'line_spacing': 98,
            'align': 'center',
            'font_size': 125,
            'shadow': 2,
            'save_path': element_dir + '/text_head.png',
        },
        {
            'text_type': 'content',
            'text': content_text,
            'font_path': font_dir + '/FC Minimal Regular.otf',
            'text_color': (255, 255, 255),
            'bg_color': (0, 0, 0),
            'img_width': 1709,
            'img_height': 729,
            'bg_alpha': 0,  # 0-255
            'line_spacing': 30,
            'align': 'center',
            'font_size': 125,
            'shadow': 4,
            'save_path': element_dir + '/text_content.png',
        },
        {
            'text_type': 'credit',
            'text': credit_text,
            'font_path': font_dir + '/FC Minimal Regular.otf',
            'text_color': (255, 255, 255),
            'bg_color': (0, 0, 0),
            'img_width': 1702,
            'img_height': 131,
            'bg_alpha': 0,  # 0-255
            'line_spacing': 0,
            'align': 'right',
            'font_size': 125,
            'shadow': 1,
            'save_path': element_dir + '/text_credit.png',
        },
    ]

    import PIL
    print('Pillow version ', PIL.__version__)
    pil_version = int(PIL.__version__[0])
    for data in render_text_rec:
        if pil_version > 8:
            imgen.render_text(data['text'], data['font_path'], data['text_color'], data['bg_color'],
                              data['img_width'], data['img_height'], data['bg_alpha'], data['line_spacing'],
                              data['align'],
                              save_path=data['save_path'], max_size=data['font_size'], shadow_offset=data['shadow'])
        else:
            imgen.render_text_legacy(data['text'], data['font_path'], data['text_color'], data['bg_color'],
                              data['img_width'], data['img_height'], data['bg_alpha'], data['line_spacing'],
                              data['align'],
                              save_path=data['save_path'], max_size=data['font_size'], shadow_offset=data['shadow'])
    out_path = imgen.create_quote_image()
    return out_path

if __name__ == '__main__':
    run(
        head_text='Animation Workflow and Reference',
        content_text='Emphasizing the importance of reference \nin the animation process to explore \nand answer questions upfront, \nmaking the workflow more efficient \nand avoiding potential issues later on.',
        credit_text='Unknown'
    )