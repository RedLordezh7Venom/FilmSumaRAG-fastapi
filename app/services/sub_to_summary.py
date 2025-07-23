from app.utils.subliminal_downloader import download_subs
from app.utils.srt_processor import process as process_srt
from app.utils.file_operations import detect_encoding, split_text_into_chunks, delete_files
from app.services.gemini_service import generate_summary
import os

async def get_movie_summary(moviename: str):
    vidfile = moviename + ".mp4"
    subfile = moviename + ".en.srt"
    final_file = moviename + ".en_text.txt"

    # Create dummy videofile for subliminal subs
    with open(vidfile, "wb") as f:
        pass

    # Download subtitles
    print("Downloading subtitles...")
    download_subs(vidfile)

    # Process subtitles
    print("Processing subtitles...")
    process_srt(subfile)
    encoding = detect_encoding(final_file)

    # Split text into chunks
    print("Splitting text into chunks...")
    chunks = split_text_into_chunks(final_file, encoding)

    delete_files([vidfile, subfile, final_file])
    print("Generating summary...")
    summary = await generate_summary(chunks)

    return summary
