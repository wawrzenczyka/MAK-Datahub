from django.core.files.storage import FileSystemStorage

def save_file(f, filename):
    fs = FileSystemStorage()
    fs.save(filename, f)
    return fs.url(filename)
    
def get_file(file_id):
    with open(file_id, 'rb') as f:
        return f.read()