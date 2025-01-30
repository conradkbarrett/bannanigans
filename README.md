# Bannanigans - Image Banner Generator

A serverless web application that adds customizable banners to images. Built with Netlify Functions, Python, and JavaScript.

## Features

- Upload images and add custom banners
- Customize banner text, position, and colors
- Real-time preview
- Responsive design
- Serverless architecture

## Tech Stack

- Frontend: HTML, CSS, JavaScript
- Backend: Netlify Functions (Node.js + Python)
- Image Processing: Python (Pillow)
- Hosting: Netlify

## Project Structure

```
.
├── functions/
│   └── process/
│       ├── index.js          # Node.js function wrapper
│       ├── process.py        # Python image processing
│       ├── requirements.txt  # Python dependencies
│       └── fonts/           # Custom fonts
├── index.html               # Main application
├── netlify.toml            # Netlify configuration
└── README.md
```

## Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/conradkbarrett/bannanigans.git
   cd bannanigans
   ```

2. Install dependencies:
   ```bash
   # Install Python dependencies
   cd functions/process
   pip install -r requirements.txt
   cd ../..
   ```

3. Install Netlify CLI:
   ```bash
   npm install -g netlify-cli
   ```

4. Start local development server:
   ```bash
   netlify dev
   ```

5. Open http://localhost:8888 in your browser

## Deployment

1. Connect your GitHub repository to Netlify
2. Configure the following environment variables in Netlify:
   - `PYTHON_VERSION`: 3.9
   - `NODE_VERSION`: 18

3. Deploy with the following settings:
   - Build command: none required
   - Publish directory: .
   - Functions directory: functions

## API Endpoints

### POST /.netlify/functions/process

Adds a banner to an image.

Request body:
```json
{
  "image": "base64_encoded_image",
  "banner_text": ["Line 1", "Line 2"],
  "banner_position": "top|bottom",
  "text_align": "left|center|right",
  "font_size": 40,
  "text_color": "#FFFFFF",
  "banner_color": "#000000"
}
```

Response:
```json
{
  "status": "success",
  "image": "base64_encoded_result"
}
```

## License

MIT License - feel free to use this project for your own purposes.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
