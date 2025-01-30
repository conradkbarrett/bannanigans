import os
import requests

def download_font(weight, is_italic=False):
    # Create fonts directory if it doesn't exist
    os.makedirs('static/fonts', exist_ok=True)
    
    # Determine filename
    if weight == 'regular':
        base_name = 'Poppins-Regular' if not is_italic else 'Poppins-Italic'
    else:
        weight_name = weight.capitalize()
        base_name = f'Poppins-{weight_name}' if not is_italic else f'Poppins-{weight_name}Italic'
    
    filename = f'{base_name}.ttf'
    filepath = os.path.join('static/fonts', filename)
    
    # Skip if file already exists
    if os.path.exists(filepath):
        print(f"Font {filename} already exists")
        return
    
    # GitHub raw content URL for Poppins fonts
    url = f"https://github.com/google/fonts/raw/main/ofl/poppins/{filename}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded {filename}")
    except Exception as e:
        print(f"Failed to download {filename}: {str(e)}")

# Download all weights
weights = ['thin', 'extralight', 'light', 'regular', 'medium', 'semibold', 'bold', 'extrabold', 'black']

for weight in weights:
    # Download regular version
    download_font(weight)
    # Download italic version
    download_font(weight, is_italic=True)

print("Font download complete!") 