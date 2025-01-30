import json
import os
import sys
import traceback
import uuid

def handler(event, context):
    """Test function to verify Netlify setup"""
    
    # Generate request ID for tracking
    request_id = str(uuid.uuid4())[:8]
    
    # Debug: Log full event data
    print(f"\n{'='*50}")
    print(f"[{request_id}] Test function called")
    print(f"[{request_id}] Request method: {event.get('httpMethod')}")
    print(f"[{request_id}] Request path: {event.get('path')}")
    print(f"[{request_id}] Headers: {json.dumps(event.get('headers', {}), indent=2)}")
    print(f"{'='*50}")
    
    # Common headers for all responses
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET, OPTIONS',
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
        print(f"\n[{request_id}] === Gathering Environment Info ===")
        # Get environment information
        env_info = {
            'pwd': os.getcwd(),
            'files': os.listdir('.'),
            'python_path': os.getenv('PYTHONPATH', 'not set'),
            'python_version': sys.version,
            'event_method': event.get('httpMethod', 'not set'),
            'event_path': event.get('path', 'not set'),
            'event_headers': event.get('headers', {}),
            'event_queryStringParameters': event.get('queryStringParameters', {}),
            'event_body': event.get('body', 'not set')
        }
        
        print(f"[{request_id}] Environment details:")
        print(f"[{request_id}] - Working directory: {env_info['pwd']}")
        print(f"[{request_id}] - Python version: {env_info['python_version'].split()[0]}")
        print(f"[{request_id}] - PYTHONPATH: {env_info['python_path']}")
        print(f"[{request_id}] - Files in directory: {', '.join(env_info['files'])}")

        print(f"\n[{request_id}] === Finalizing ===")
        print(f"[{request_id}] Test function completed successfully")
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'status': 'success',
                'message': 'Test function is working',
                'environment': env_info,
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