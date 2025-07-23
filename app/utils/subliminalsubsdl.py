import subliminal
from subliminal import save_subtitles
from babelfish import Language
from pathlib import Path
import os
import tempfile

def download_subs(movie_file):
    video = subliminal.scan_video(movie_file)

    subtitles = subliminal.download_best_subtitles([video], {Language('eng')})

    # Save the subtitle to a file
    if subtitles and video in subtitles:
        save_subtitles(video, subtitles[video])
        print(f"Subtitles downloaded and saved as {Path(movie_file).stem}.en.srt")
    else:
        print("No subtitles found for the given movie.")

def create_temp_mp4_and_download_subs(movie_file_path):
    """
    Creates a temporary directory, copies the movie file into it,
    and downloads subtitles for it within that temporary directory.
    Returns the path to the temporary directory.
    """
    temp_base_dir = Path("app") / "temp_files"
    temp_base_dir.mkdir(parents=True, exist_ok=True)
    temp_dir = tempfile.mkdtemp(dir=temp_base_dir)
    print(f"Created temporary directory: {temp_dir}")

    # Copy the movie file to the temporary directory
    temp_movie_path = Path(temp_dir) / Path(movie_file_path).name
    import shutil
    shutil.copy(movie_file_path, temp_movie_path)
    print(f"Copied '{movie_file_path}' to '{temp_movie_path}'")

    # Download subtitles to the temporary directory (they will be saved next to temp_movie_path)
    download_subs(str(temp_movie_path))
    
    return temp_dir
