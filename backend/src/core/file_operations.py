import os
import logging
import hashlib
import filecmp
import datetime
import shutil
import re
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm
import librosa


# Setting up logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FileOperations:
    """Class provides all filesystem operations"""

    def __init__(self):
        None

    def _get_file_content_hash_full(self, filepath):
        hasher = hashlib.sha1()
        with open(filepath, 'rb') as f:
            buf = f.read(65536)
            while buf:
                hasher.update(buf)
                buf = f.read(65536)
        return hasher.hexdigest()

    def _get_file_content_hash_sample(self, filepath):
        """
        Generates a hash for a file by sampling parts of the file.
        sample_size specifies the block size to read.
        """
        file_size = os.path.getsize(filepath)
        hash_obj = hashlib.sha256()
        sample_size = 256
        
        with open(filepath, 'rb') as f:
            # Include file size in the hash
            hash_obj.update(str(file_size).encode())

            # If the file is smaller than twice the sample_size, just read it once
            if file_size <= 2 * sample_size:
                hash_obj.update(f.read())
            else:
                # Read the start, middle, and end of the file
                f.seek(0)
                hash_obj.update(f.read(sample_size))
                f.seek(file_size // 2)
                hash_obj.update(f.read(sample_size))
                f.seek(-sample_size, os.SEEK_END)
                hash_obj.update(f.read(sample_size))

        return hash_obj.hexdigest()
    
    def get_file_metadata_hash(self, filepath):
        metadata = self.get_file_metadata(filepath)  # Assuming get_file_metadata is also a static method
        combined_hash = str(str(metadata['hash']) + str(metadata['size']) + metadata['creation_time'])
        return hashlib.sha1(combined_hash.encode()).hexdigest()
    
    def get_file_metadata(self, filepath):
        """Prepare file data for further processing or storage."""
        # Get file size, modification time, and other relevant metadata
        metadata = os.stat(filepath)
        hash = self._get_file_content_hash_sample(filepath)
        mtime = datetime.datetime.fromtimestamp(metadata.st_mtime).isoformat()
        atime = datetime.datetime.fromtimestamp(metadata.st_atime).isoformat()
        ctime = datetime.datetime.fromtimestamp(metadata.st_ctime).isoformat()

        # Return a dictionary or tuple with all the prepared data
        file_data = {
            'path': filepath,
            'hash': hash,
            'size': metadata.st_size,
            'modification_time': mtime,
            'access_time': atime,
            'creation_time': ctime
        }

        return file_data

    def get_file_date(self, filepath):
        filename = os.path.basename(filepath)
        date_from_name = self.extract_date_from_filename(filename)
        if date_from_name:
            return date_from_name
        else:
            timestamp = os.path.getmtime(filepath)
            return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H.%M.%S')
    
    def extract_date_from_filename(self, filename):
        date_pattern = re.compile(r'(\d{4}-\d{2}-\d{2} \d{2}\.\d{2}\.\d{2})')
        match = date_pattern.search(filename)
        return match.group(1) if match else None
    
    def audio_duration(self, filepath):
        y, sr = librosa.load(filepath, sr=None)
        return librosa.get_duration(y=y, sr=sr)

    def find_potential_audio_duplicates_by_duration(self, directory):
        duration_map = {}
        potential_duplicates = {}
        all_files = [os.path.join(dirpath, filename) 
                    for dirpath, _, filenames in os.walk(directory) 
                    for filename in filenames if filename.endswith(('.mp3', '.wav', '.flac'))]
        for filepath in all_files:
            file_duration = self.audio_duration(filepath)
            if file_duration in duration_map:
                potential_duplicates.setdefault(file_duration, []).append(filepath)
            else:
                duration_map[file_duration] = filepath
        return {k: v for k, v in potential_duplicates.items() if len(v) > 1}

    def find_duplicates(self, directory):
        hashes = {}
        duplicates = {}
        with ProcessPoolExecutor() as executor:
            for dirpath, _, filenames in os.walk(directory):
                filepaths = [os.path.join(dirpath, filename) for filename in filenames]
                for filepath, file_hash in zip(filepaths, executor.map(FileOperations._get_file_content_hash_sample, filepaths)):
                    if file_hash in hashes:
                        duplicates.setdefault(file_hash, []).append(filepath)
                    else:
                        hashes[file_hash] = filepath
        return {k: v for k, v in duplicates.items() if len(v) > 1}

    def is_file_exist(self, file_path):
        """Check if destination file exists and is identical to the source."""
        return os.path.exists(file_path)
    
    def is_file_same(self, source, destination):
        """Check if destination file exists and is identical to the source."""
        return filecmp.cmp(source, destination, shallow=False)
        
    def move_file_with_metadata_preserved(self, source, destination):
        """Move a file and preserve its metadata."""
        try:
            if not (self.is_file_exist(source) and self.is_file_same(source, destination)):
                shutil.move(source, destination)
                if os.name in ["posix"]:
                    metadata = os.stat(destination)
                    os.utime(destination, (metadata.st_atime, metadata.st_mtime))
                logging.info("Moved %s to %s", source, destination)
            else:
                logging.warning("File %s already exists at %s and is identical. Skipping.", source, destination)
        except Exception as e:
            logging.error("Error moving %s to %s. Error: %s",source,destination, e)

    def process_and_move_files(self, file_paths, destination_directory):
        """Process files with a progress bar and then move them."""
        for file_path in tqdm(file_paths, desc="Processing and moving files"):
            destination = os.path.join(destination_directory, os.path.basename(file_path))
            self.move_file_with_metadata_preserved(file_path, destination)
