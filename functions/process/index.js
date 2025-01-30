const { execSync } = require('child_process');
const path = require('path');

exports.handler = async function(event, context) {
  // Set up CORS headers
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
  };

  // Handle OPTIONS request
  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 204,
      headers,
      body: ''
    };
  }

  try {
    // Log environment for debugging
    console.log('Current directory:', process.cwd());
    console.log('Directory contents:', execSync('ls -la').toString());
    console.log('Python version:', execSync('python3 --version').toString());

    // Execute Python script
    const scriptPath = path.join(__dirname, 'process.py');
    console.log('Script path:', scriptPath);
    
    const result = execSync(`python3 ${scriptPath}`, {
      input: event.body,
      encoding: 'utf-8',
      env: { ...process.env, PYTHONPATH: __dirname }
    });

    return {
      statusCode: 200,
      headers,
      body: result
    };
  } catch (error) {
    console.error('Error:', error);
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({
        error: 'Internal server error',
        details: error.message,
        stdout: error.stdout?.toString(),
        stderr: error.stderr?.toString()
      })
    };
  }
}; 