import os
from flask import Flask, request, render_template, send_file, jsonify
from PIL import Image, ImageDraw, ImageFont
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['FONT_FOLDER'] = os.path.join('static', 'fonts')

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['FONT_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Font weight mappings
FONT_WEIGHTS = {
    'thin': 100,
    'extralight': 200,
    'light': 300,
    'regular': 400,
    'medium': 500,
    'semibold': 600,
    'bold': 700,
    'extrabold': 800,
    'black': 900
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def calculate_banner_position(position, img_width, img_height, total_height):
    padding = 40  # Padding from top/bottom edges
    positions = {
        'top': (0, padding),
        'bottom': (0, img_height - total_height - padding),
        'middle': (0, (img_height - total_height) // 2)
    }
    return positions.get(position, (0, padding))

def calculate_text_position(position, banner_width, text_width):
    edge_padding = 10  # Reduced padding for left/right edges
    positions = {
        'left': edge_padding,
        'center': (banner_width - text_width) // 2,
        'right': banner_width - text_width - edge_padding
    }
    return positions.get(position, edge_padding)

def get_font(weight='regular', size=50, italic=False):
    """Load Poppins font with specified weight and style"""
    style = 'Italic' if italic else 'Regular'
    if weight != 'regular':
        base_name = f'Poppins-{weight.capitalize()}'
    else:
        base_name = 'Poppins-Regular'
    
    if italic and weight != 'regular':
        font_file = f'Poppins-{weight.capitalize()}Italic.ttf'
    elif italic:
        font_file = 'Poppins-Italic.ttf'
    else:
        font_file = f'{base_name}.ttf'

    font_path = os.path.join(app.config['FONT_FOLDER'], font_file)
    try:
        return ImageFont.truetype(font_path, size)
    except:
        print(f"Failed to load font: {font_path}")
        return ImageFont.load_default()

def get_text_dimensions(text, font):
    # Get the actual text dimensions including ascenders and descenders
    bbox = font.getbbox(text)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    
    # Get additional metrics
    ascent, descent = font.getmetrics()
    
    return {
        'width': width,
        'height': height,
        'ascent': ascent,
        'descent': descent,
        'total_height': ascent + descent
    }

def draw_button(draw, text, font, width, height, text_color, bg_color):
    """Draw a button with the same style as text banners"""
    # Create button background
    button = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    button_draw = ImageDraw.Draw(button)
    
    # Convert hex colors to RGBA
    bg_color = tuple(int(bg_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + (255,)
    text_color = tuple(int(text_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + (255,)
    
    # Draw rectangle (no rounded corners to match text banners)
    button_draw.rectangle([0, 0, width, height], fill=bg_color)
    
    # Get text dimensions for centering
    text_bbox = font.getbbox(text)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    # Center text vertically and horizontally
    text_x = (width - text_width) // 2
    text_y = (height - text_height) // 2
    
    # Adjust for font metrics
    metrics = font.getmetrics()
    metrics_adjustment = (metrics[1] - metrics[0]) // 4
    text_y += metrics_adjustment
    
    # Draw text
    button_draw.text((text_x, text_y), text, font=font, fill=text_color)
    
    return button

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'image' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400

    try:
        # Save the original image
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Get banner parameters from form
        banner_text = [text for text in request.form.getlist('banner_text[]') if text.strip()]
        font_weight = request.form.get('font_weight', 'regular')
        font_size = int(request.form.get('font_size', 40))
        is_italic = 'italic' in request.form.getlist('font_style[]')
        text_color = request.form.get('text_color', '#FFFFFF')
        banner_color = request.form.get('banner_color', '#000000')
        banner_position = request.form.get('banner_position', 'top')
        text_align = request.form.get('text_align', 'left')

        # Process the image
        img = Image.open(filepath)
        
        # Get font with specified style
        font = get_font(weight=font_weight, size=font_size, italic=is_italic)

        # Calculate total height and get text dimensions
        vertical_padding = int(font_size * 0.1)  # Reduced to 10% of font size for tighter vertical spacing
        line_padding = int(font_size * 0.1)  # Space between text blocks also reduced
        total_height = 0
        text_blocks = []

        for text in banner_text:
            # Get precise text dimensions
            dims = get_text_dimensions(text, font)
            block_height = dims['total_height'] + (vertical_padding * 2)  # Add minimal padding above and below
            
            text_blocks.append({
                'text': text,
                'width': dims['width'],
                'height': block_height,
                'text_height': dims['height'],
                'ascent': dims['ascent'],
                'descent': dims['descent'],
                'y_offset': total_height
            })
            total_height += block_height + line_padding

        # Remove last line padding
        if text_blocks:
            total_height -= line_padding

        # Calculate starting position for the entire text block
        banner_x, banner_y = calculate_banner_position(banner_position, img.width, img.height, total_height)

        # Create result image
        result = Image.new('RGBA', (img.width, img.height))
        result.paste(img, (0, 0))

        # Draw each text block
        for block in text_blocks:
            # Calculate banner width for this specific text
            horizontal_padding = 10  # Fixed small padding for horizontal edges
            banner_width = block['width'] + (horizontal_padding * 2)

            # Create individual banner for this line
            banner = Image.new('RGBA', (banner_width, block['height']), banner_color)
            draw = ImageDraw.Draw(banner)

            # Calculate text position within this banner
            text_x = calculate_text_position(text_align, banner_width, block['width'])
            # Center text vertically using ascent and descent
            text_y = (block['height'] - block['text_height']) // 2

            # Adjust text_y to account for font metrics and achieve optical centering
            metrics_adjustment = (block['descent'] - block['ascent']) // 4  # Fine-tune vertical position
            text_y += metrics_adjustment

            # Draw text
            draw.text((text_x, text_y), block['text'], font=font, fill=text_color)

            # Calculate x position for banner
            if text_align == 'center':
                banner_offset_x = (img.width - banner_width) // 2
            elif text_align == 'right':
                banner_offset_x = img.width - banner_width
            else:  # left
                banner_offset_x = 0

            # Paste this banner onto result
            result.paste(banner, (banner_offset_x, banner_y + block['y_offset']), banner)

        # Save result
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], f'processed_{filename}')
        result.save(output_path)

        return jsonify({
            'success': True,
            'filename': f'processed_{filename}'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename),
                    as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=8080) 