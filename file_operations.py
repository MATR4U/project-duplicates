import os
import hashlib
import filecmp
import datetime
from concurrent.futures import ProcessPoolExecutor
import librosa
from tqdm import tqdm
import shutil
import logging
import re

# Setting up logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FileOperations:
    def __init__(self, dataSourceDirectory, dataDestinationDir):
        self.dataSourceDirectory = dataSourceDirectory
        self.dataDestinationDir = dataDestinationDir

    @staticmethod
    def _get_file_content_hash_full(filepath):
        hasher = hashlib.sha1()
        with open(filepath, 'rb') as f:
            buf = f.read(65536)
            while buf:
                hasher.update(buf)
                buf = f.read(65536)
        return hasher.hexdigest()

    @staticmethod
    def _get_file_content_hash_sample(filepath):
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
    
    @staticmethod
    def get_file_metadata_hash(filepath):
        metadata = FileOperations.get_file_metadata(filepath)  # Assuming get_file_metadata is also a static method
        combined_hash = str(str(metadata['hash']) + str(metadata['size']) + metadata['creation_time'])
        return hashlib.sha1(combined_hash.encode()).hexdigest()
    
    @staticmethod
    def get_file_metadata(filepath):
        """Prepare file data for further processing or storage."""
        # Get file size, modification time, and other relevant metadata
        metadata = os.stat(filepath)
        hash = FileOperations._get_file_content_hash_sample(filepath)
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

    @staticmethod
    def get_file_date(filepath):
        filename = os.path.basename(filepath)
        date_from_name = FileOperations.extract_date_from_filename(filename)
        if date_from_name:
            return date_from_name
        else:
            timestamp = os.path.getmtime(filepath)
            return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H.%M.%S')
        
    @staticmethod
    def extract_date_from_filename(filename):
        date_pattern = re.compile(r'(\d{4}-\d{2}-\d{2} \d{2}\.\d{2}\.\d{2})')
        match = date_pattern.search(filename)
        return match.group(1) if match else None
    
    @staticmethod
    def audio_duration(filepath):
        y, sr = librosa.load(filepath, sr=None)
        return librosa.get_duration(y=y, sr=sr)

    @staticmethod
    def find_potential_audio_duplicates_by_duration(directory):
        duration_map = {}
        potential_duplicates = {}
        all_files = [os.path.join(dirpath, filename) 
                    for dirpath, _, filenames in os.walk(directory) 
                    for filename in filenames if filename.endswith(('.mp3', '.wav', '.flac'))]
        for filepath in all_files:
            file_duration = FileOperations.audio_duration(filepath)
            if file_duration in duration_map:
                potential_duplicates.setdefault(file_duration, []).append(filepath)
            else:
                duration_map[file_duration] = filepath
        return {k: v for k, v in potential_duplicates.items() if len(v) > 1}

    @staticmethod
    def find_duplicates(directory):
        hashes = {}
        duplicates = {}
        with ProcessPoolExecutor() as executor:
            for dirpath, _, filenames in os.walk(directory):
                filepaths = [os.path.join(dirpath, filename) for filename in filenames]
                for filepath, file_hash in zip(filepaths, executor.map(FileOperations.get_hash_filecontent, filepaths)):
                    if file_hash in hashes:
                        duplicates.setdefault(file_hash, []).append(filepath)
                    else:
                        hashes[file_hash] = filepath
        return {k: v for k, v in duplicates.items() if len(v) > 1}

    @staticmethod
    def file_exists_and_same(source, destination):
        """Check if destination file exists and is identical to the source."""
        if os.path.exists(destination):
            return filecmp.cmp(source, destination, shallow=False)
        return False

    @staticmethod
    def move_file_with_metadata_preserved(source, destination):
        """Move a file and preserve its metadata."""
        try:
            if not FileOperations.file_exists_and_same(source, destination):
                shutil.move(source, destination)
                if os.name in ["posix"]:
                    metadata = os.stat(destination)
                    os.utime(destination, (metadata.st_atime, metadata.st_mtime))
                logging.info(f"Moved {source} to {destination}")
            else:
                logging.warning(f"File {source} already exists at {destination} and is identical. Skipping.")
        except Exception as e:
            logging.error(f"Error moving {source} to {destination}. Error: {str(e)}")

    @staticmethod
    def process_and_move_files(file_paths, destination_directory):
        """Process files with a progress bar and then move them."""
        for file_path in tqdm(file_paths, desc="Processing and moving files"):
            destination = os.path.join(destination_directory, os.path.basename(file_path))
            FileOperations.move_file_with_metadata_preserved(file_path, destination)
