import os
import json
import sys
import pkg_resources
import traceback

def handler(event, context):
    """Basic test function"""
    
    # Debug logging
    print(f"Event: {json.dumps(event)}")
    print(f"Context: {json.dumps(context.__dict__ if context else {})}")
    print(f"Environment: PYTHON_VERSION={os.environ.get('PYTHON_VERSION')}")
    
    try:
        # Get installed packages for debugging
        installed_packages = [f"{dist.key} {dist.version}" for dist in pkg_resources.working_set]
        print(f"Installed packages: {', '.join(installed_packages)}")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': os.environ.get('ALLOWED_ORIGINS', '*'),
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET, OPTIONS',
            },
            'body': json.dumps({
                'status': 'success',
                'message': 'Function is running',
                'python_version': sys.version,
                'packages': installed_packages,
                'env_vars': {
                    'PYTHON_VERSION': os.environ.get('PYTHON_VERSION'),
                    'DEBUG': os.environ.get('DEBUG'),
                    'FUNCTION_DEBUG': os.environ.get('FUNCTION_DEBUG')
                }
            })
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': os.environ.get('ALLOWED_ORIGINS', '*')
            },
            'body': json.dumps({
                'status': 'error',
                'error': str(e),
                'traceback': traceback.format_exc()
            })
        } 