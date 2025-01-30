from PIL import Image, ImageDraw, ImageFont
import json
import base64
from io import BytesIO
import os
import traceback
import uuid

def handler(event, context):
    """Image processing function"""
    
    # Generate request ID for tracking
    request_id = str(uuid.uuid4())[:8]
    
    # Debug: Log full event data
    print(f"\n{'='*50}")
    print(f"[{request_id}] Image function called")
    print(f"[{request_id}] Request method: {event.get('httpMethod')}")
    print(f"[{request_id}] Request path: {event.get('path')}")
    print(f"[{request_id}] Headers: {json.dumps(event.get('headers', {}), indent=2)}")
    print(f"{'='*50}")
    
    # Common headers for all responses
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Max-Age': '86400',
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
        if not event.get('body'):
            print(f"[{request_id}] ERROR: No request body provided")
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    'status': 'error',
                    'error': 'No request body provided',
                    'request_id': request_id
                })
            }
            
        try:
            body = json.loads(event.get('body'))
            print(f"[{request_id}] Body keys present: {list(body.keys())}")
        except json.JSONDecodeError as e:
            print(f"[{request_id}] ERROR: Failed to parse JSON body")
            print(f"[{request_id}] Error details: {str(e)}")
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    'status': 'error',
                    'error': 'Invalid JSON in request body',
                    'details': str(e),
                    'request_id': request_id
                })
            }

        print(f"\n[{request_id}] === Processing Request ===")
        # Process the request based on body content
        print(f"[{request_id}] Processing request with body keys: {list(body.keys())}")
        
        # Add your image processing logic here
        # For now, just return success
        print(f"\n[{request_id}] === Finalizing ===")
        print(f"[{request_id}] Request processed successfully")
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'status': 'success',
                'message': 'Request processed successfully',
                'request_id': request_id
            })
        }
        
    except Exception as e:
        print(f"\n[{request_id}] === ERROR ===")
        print(f"[{request_id}] Error type: {type(e).__name__}")
        print(f"[{request_id}] Error message: {str(e)}")
        print(f"[{request_id}] Traceback:")
        print(traceback.format_exc())
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'status': 'error',
                'error': str(e),
                'error_type': type(e).__name__,
                'traceback': traceback.format_exc(),
                'request_id': request_id
            })
        } 