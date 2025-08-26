#!/usr/bin/env python3
"""
Add the missing /data route to serve images from the data directory
"""

# Read the main.py file
with open('/home/ubuntu/minds-eye-recovery/src/main.py', 'r') as f:
    content = f.read()

# Find the location to insert the new route (after the about route)
about_route_line = "@app.route('/assets/about/<filename>')"
if about_route_line in content:
    # Insert the new /data route after the about route
    new_route = '''
@app.route('/data/<filename>')
def serve_data_image(filename):
    """Serve images from the data directory (portfolio and about images)"""
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    return send_from_directory(data_dir, filename)
'''
    
    # Find the end of the serve_about_image function
    insert_pos = content.find("return send_from_directory(about_dir, filename)")
    if insert_pos != -1:
        # Find the end of that line
        insert_pos = content.find("\n", insert_pos) + 1
        
        # Insert the new route
        content = content[:insert_pos] + new_route + content[insert_pos:]
        
        # Write back to the file
        with open('/home/ubuntu/minds-eye-recovery/src/main.py', 'w') as f:
            f.write(content)
        
        print("✅ Added /data route to Flask application")
    else:
        print("❌ Could not find insertion point")
else:
    print("❌ Could not find about route")

