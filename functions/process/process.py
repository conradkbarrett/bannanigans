from PIL import Image, ImageDraw, ImageFont
import json
import base64
from io import BytesIO
import os
import traceback
import uuid

# Netlify function handler
def handler(event, context):
    """Process image and add banner text"""
    
    # Generate request ID for tracking
    request_id = str(uuid.uuid4())[:8]
    
    # Debug: Log full event data
    print(f"\n{'='*50}")
    print(f"[{request_id}] Process function called")
    print(f"[{request_id}] Request method: {event.get('httpMethod')}")
    print(f"[{request_id}] Request path: {event.get('path')}")
    print(f"[{request_id}] Headers: {json.dumps(event.get('headers', {}), indent=2)}")
    print(f"[{request_id}] Query parameters: {json.dumps(event.get('queryStringParameters', {}), indent=2)}")
    print(f"[{request_id}] Current directory: {os.getcwd()}")
    print(f"[{request_id}] Directory contents: {os.listdir('.')}")
    print(f"[{request_id}] Environment variables: {json.dumps(dict(os.environ), indent=2)}")
    print(f"{'='*50}")
    
    # Common headers for all responses
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'X-Request-ID': request_id
    }
    
    # Handle OPTIONS request for CORS
    if event.get('httpMethod') == 'OPTIONS':
        print(f"[{request_id}] Handling OPTIONS request")
        return {
            'statusCode': 204,
            'headers': headers,
            'body': ''
        }
    
    try:
        print(f"\n[{request_id}] === Parsing Request Body ===")
        body = event.get('body', '')
        print(f"[{request_id}] Raw body type: {type(body)}")
        print(f"[{request_id}] Raw body length: {len(str(body))}")
        print(f"[{request_id}] Raw body preview: {str(body)[:200]}...")

        if not body:
            print(f"[{request_id}] ERROR: No request body provided")
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    'error': 'No request body provided',
                    'request_id': request_id
                })
            }

        try:
            # If body is already a dict, use it directly
            if isinstance(body, dict):
                parsed_body = body
            else:
                parsed_body = json.loads(body)
            print(f"[{request_id}] Body keys present: {list(parsed_body.keys())}")
        except json.JSONDecodeError as e:
            print(f"[{request_id}] ERROR: Failed to parse JSON body")
            print(f"[{request_id}] Error details: {str(e)}")
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    'error': 'Invalid JSON in request body',
                    'details': str(e),
                    'request_id': request_id
                })
            }

        # Get image data
        image_data = parsed_body.get('image')
        if not image_data:
            print(f"[{request_id}] ERROR: No image data in request")
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    'error': 'No image data provided',
                    'request_id': request_id
                })
            }

        # Remove data URL prefix if present
        if image_data.startswith('data:image'):
            image_data = image_data.split(',')[1]

        # Process image
        try:
            # Decode base64 image
            image_bytes = base64.b64decode(image_data)
            image = Image.open(BytesIO(image_bytes))
            print(f"[{request_id}] Successfully loaded image: size={image.size}, mode={image.mode}")
            
            # Get banner parameters
            banner_text = parsed_body.get('banner_text', [])
            banner_position = parsed_body.get('banner_position', 'bottom')
            text_align = parsed_body.get('text_align', 'center')
            font_size = int(parsed_body.get('font_size', 40))
            text_color = parsed_body.get('text_color', '#FFFFFF')
            banner_color = parsed_body.get('banner_color', '#000000')
            
            print(f"[{request_id}] Banner parameters:")
            print(f"[{request_id}] - Text: {banner_text}")
            print(f"[{request_id}] - Position: {banner_position}")
            print(f"[{request_id}] - Alignment: {text_align}")
            print(f"[{request_id}] - Font size: {font_size}")
            print(f"[{request_id}] - Colors: text={text_color}, banner={banner_color}")
            
            # Try to load font
            try:
                font_path = os.path.join(os.path.dirname(__file__), 'fonts', 'Poppins-Bold.ttf')
                print(f"[{request_id}] Looking for font at: {font_path}")
                print(f"[{request_id}] Directory contents: {os.listdir(os.path.dirname(__file__))}")
                if os.path.exists(font_path):
                    print(f"[{request_id}] Font file found")
                    font = ImageFont.truetype(font_path, font_size)
                else:
                    print(f"[{request_id}] Font file not found, using default font")
                    font = ImageFont.load_default()
            except Exception as e:
                print(f"[{request_id}] Error loading font: {str(e)}")
                print(f"[{request_id}] Using default font")
                font = ImageFont.load_default()

            # Calculate banner dimensions
            banner_height = font_size * (len(banner_text) + 1)
            banner_width = image.width

            # Create banner
            banner = Image.new('RGBA', (banner_width, banner_height), banner_color)
            draw = ImageDraw.Draw(banner)

            # Draw text
            y_offset = font_size // 2
            for text in banner_text:
                if text:
                    text_bbox = draw.textbbox((0, 0), text, font=font)
                    text_width = text_bbox[2] - text_bbox[0]
                    
                    if text_align == 'center':
                        x = (banner_width - text_width) // 2
                    elif text_align == 'right':
                        x = banner_width - text_width - font_size
                    else:  # left
                        x = font_size

                    draw.text((x, y_offset), text, fill=text_color, font=font)
                    y_offset += font_size

            # Combine images
            new_height = image.height + banner_height
            combined = Image.new('RGB', (image.width, new_height), banner_color)
            
            if banner_position == 'top':
                combined.paste(banner, (0, 0))
                combined.paste(image, (0, banner_height))
            else:  # bottom
                combined.paste(image, (0, 0))
                combined.paste(banner, (0, image.height))

            # Save result
            buffer = BytesIO()
            combined.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            print(f"[{request_id}] Successfully processed image")
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    'status': 'success',
                    'image': f'data:image/png;base64,{img_str}',
                    'request_id': request_id
                })
            }
            
        except Exception as e:
            print(f"[{request_id}] Error processing image: {str(e)}")
            print(f"[{request_id}] Traceback: {traceback.format_exc()}")
            return {
                'statusCode': 500,
                'headers': headers,
                'body': json.dumps({
                    'error': f'Error processing image: {str(e)}',
                    'traceback': traceback.format_exc(),
                    'request_id': request_id
                })
            }
            
    except Exception as e:
        print(f"[{request_id}] Unexpected error: {str(e)}")
        print(f"[{request_id}] Traceback: {traceback.format_exc()}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': str(e),
                'traceback': traceback.format_exc(),
                'request_id': request_id
            })
        }

# Make handler available to Netlify
def main(event, context):
    return handler(event, context) 