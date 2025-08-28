# Add this endpoint to main.py to show /data directory contents

@app.route('/debug/data-contents')
def show_data_contents():
    """Show all contents of /data directory"""
    import os
    import json
    from datetime import datetime
    
    data_dir = '/data'
    result = {
        'directory': data_dir,
        'exists': os.path.exists(data_dir),
        'files': [],
        'total_files': 0,
        'checked_at': datetime.now().isoformat()
    }
    
    if os.path.exists(data_dir):
        try:
            all_files = os.listdir(data_dir)
            result['total_files'] = len(all_files)
            
            for filename in sorted(all_files):
                filepath = os.path.join(data_dir, filename)
                file_info = {
                    'name': filename,
                    'size': os.path.getsize(filepath) if os.path.isfile(filepath) else 0,
                    'is_file': os.path.isfile(filepath),
                    'is_dir': os.path.isdir(filepath)
                }
                
                # If it's a JSON file, try to read its contents
                if filename.endswith('.json') and os.path.isfile(filepath):
                    try:
                        with open(filepath, 'r') as f:
                            file_info['json_content'] = json.load(f)
                    except:
                        file_info['json_content'] = 'Error reading JSON'
                
                result['files'].append(file_info)
                
        except Exception as e:
            result['error'] = str(e)
    
    return f"<pre>{json.dumps(result, indent=2)}</pre>"

