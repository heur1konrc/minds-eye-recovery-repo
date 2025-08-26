#!/usr/bin/env python3

# Script to replace the broken About page function with a clean version

import re

# Read the current main.py
with open('src/main.py', 'r') as f:
    content = f.read()

# Find the start and end of the about_page function
lines = content.split('\n')
start_line = None
end_line = None

for i, line in enumerate(lines):
    if line.strip() == 'def about_page():':
        start_line = i
    elif start_line is not None and (line.startswith('@app.route') or line.startswith('def ')) and i > start_line:
        end_line = i
        break

if start_line is not None and end_line is not None:
    print(f"Found about_page function from line {start_line+1} to {end_line}")
    
    # Create the new clean function
    new_function = '''def about_page():
    """Clean About page using Image table with is_about flag"""
    try:
        from src.models import Image
        about_images = Image.query.filter(Image.is_about == True).order_by(Image.display_order.asc(), Image.upload_date.asc()).all()
        first_about_image = about_images[0] if about_images else None
        
        if first_about_image:
            image_html = f'<img src="/data/{first_about_image.filename}" alt="{first_about_image.title}" class="w-full h-full object-cover">'
            image_title = first_about_image.title
        else:
            image_html = '<div class="w-full h-full bg-gradient-to-br from-green-600 to-green-800 flex items-center justify-center"><p class="text-white text-center font-semibold">Behind the Lens Image<br/>Will appear here once uploaded</p></div>'
            image_title = "Behind the Lens"
        
        return f\'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>About - Mind's Eye Photography</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {{ background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%); min-height: 100vh; }}
    </style>
</head>
<body class="text-white">
    <nav class="bg-black bg-opacity-50 p-4">
        <div class="container mx-auto flex justify-between items-center">
            <a href="/" class="text-2xl font-bold text-orange-400">Mind's Eye Photography</a>
            <div class="space-x-6">
                <a href="/" class="hover:text-orange-400 transition-colors">Home</a>
                <a href="/portfolio" class="hover:text-orange-400 transition-colors">Portfolio</a>
                <a href="/featured" class="hover:text-orange-400 transition-colors">Featured</a>
                <a href="/about" class="text-orange-400">About</a>
                <a href="/contact" class="hover:text-orange-400 transition-colors">Contact</a>
            </div>
        </div>
    </nav>
    <div class="container mx-auto px-4 py-12">
        <h1 class="text-5xl font-bold text-center text-orange-400 mb-4">About Mind's Eye Photography</h1>
        <p class="text-xl text-center text-gray-300 mb-12">Where Moments Meet Imagination</p>
        <div class="max-w-4xl mx-auto">
            <div class="float-left mr-6 mb-4 w-80 h-52 rounded-lg overflow-hidden shadow-2xl">
                {image_html}
            </div>
            <p class="text-center text-orange-400 font-semibold mb-4">{image_title}</p>
            <div class="text-lg leading-relaxed">
                <p class="mb-6">Born and raised right here in Madison, Wisconsin, I'm a creative spirit with a passion for bringing visions to life. My journey has woven through various rewarding paths – as a <strong>musician/songwriter</strong>, a <strong>Teacher</strong>, a <strong>REALTOR</strong>, and a <strong>Small Business Owner</strong>. Each of these roles has fueled my inspired, creative, and driven approach to everything I do, especially when it comes to photography.</p>
                <p class="mb-6">At the heart of Mind's Eye Photography: Where Moments Meet Imagination is my dedication to you. While I cherish the fulfillment of capturing moments that spark my own imagination, my true passion lies in doing the same for my clients. Based in Madison, I frequently travel across the state, always on the lookout for that next inspiring scene.</p>
                <p class="mb-6">For me, client satisfaction isn't just a goal – it's the foundation of every interaction. I pour my energy into ensuring you not only love your photos but also enjoy the entire experience. It's truly rewarding to see clients transform into lifelong friends, and that's the kind of connection I strive to build with everyone I work with.</p>
                <p class="text-right text-orange-400 font-semibold text-xl mt-8">Rick Corey</p>
            </div>
            <div class="clear-both"></div>
        </div>
    </div>
</body>
</html>\'''
    except Exception as e:
        return f"Error: {str(e)}", 500


'''
    
    # Replace the function
    new_lines = lines[:start_line] + new_function.split('\n') + lines[end_line:]
    new_content = '\n'.join(new_lines)
    
    # Write back to file
    with open('src/main.py', 'w') as f:
        f.write(new_content)
    
    print("Successfully replaced about_page function!")
else:
    print("Could not find about_page function boundaries")

