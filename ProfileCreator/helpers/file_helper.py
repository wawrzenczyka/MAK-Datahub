from typing import IO
import io
import os, shutil

def is_opened_binary(stream: IO) -> bool:
    return isinstance(stream, (io.RawIOBase, io.BufferedIOBase))

def is_opened_text(stream: IO) -> bool:
    return isinstance(stream, io.TextIOBase)

def clear_dir(dir_path: str):
    for filename in os.listdir(dir_path):
        file_path = os.path.join(dir_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))