import pytest
import os
from unittest.mock import patch, mock_open
from app.services.gemini_service import generate_summary
from app.services.subtitle_service import get_movie_summary
from app.utils.file_operations import detect_encoding, split_text_into_chunks, delete_files
from app.utils.srt_processor import extract_text_from_srt, process as process_srt
from app.utils.subliminal_downloader import download_subs

# Mock for generate_summary
@pytest.fixture
def mock_gemini_generate_content():
    with patch('app.services.gemini_service.model.generate_content') as mock:
        mock.return_value.text = "Mocked summary part."
        yield mock

# Mock for subtitle_service dependencies
@pytest.fixture
def mock_subtitle_service_deps():
    with patch('app.utils.subliminal_downloader.download_subs'), \
         patch('app.utils.srt_processor.process') as mock_process_srt, \
         patch('app.utils.file_operations.detect_encoding') as mock_detect_encoding, \
         patch('app.utils.file_operations.split_text_into_chunks') as mock_split_text_into_chunks, \
         patch('app.utils.file_operations.delete_files') as mock_delete_files, \
         patch('builtins.open', mock_open()):
        
        mock_process_srt.return_value = None
        mock_detect_encoding.return_value = 'utf-8'
        mock_split_text_into_chunks.return_value = ["chunk1", "chunk2"]
        mock_delete_files.return_value = None
        yield mock_process_srt, mock_detect_encoding, mock_split_text_into_chunks, mock_delete_files

@pytest.mark.asyncio
async def test_generate_summary(mock_gemini_generate_content):
    chunks = ["test chunk 1", "test chunk 2"]
    summary = await generate_summary(chunks)
    assert summary == "Mocked summary part.Mocked summary part."
    assert mock_gemini_generate_content.call_count == len(chunks)

@pytest.mark.asyncio
async def test_get_movie_summary_success(mock_subtitle_service_deps, mock_gemini_generate_content):
    moviename = "test_movie"
    summary = await get_movie_summary(moviename)
    assert summary == "Mocked summary part.Mocked summary part."
    mock_subtitle_service_deps[0].assert_called_once_with(f"{moviename}.en.srt") # process_srt
    mock_subtitle_service_deps[1].assert_called_once_with(f"{moviename}.en_text.txt") # detect_encoding
    mock_subtitle_service_deps[2].assert_called_once_with(f"{moviename}.en_text.txt", 'utf-8') # split_text_into_chunks
    mock_subtitle_service_deps[3].assert_called_once_with([f"{moviename}.mp4", f"{moviename}.en.srt", f"{moviename}.en_text.txt"]) # delete_files
    mock_gemini_generate_content.assert_called()

def test_detect_encoding():
    # Create a dummy file for testing
    test_file_path = "test_encoding.txt"
    with open(test_file_path, "w", encoding="utf-8") as f:
        f.write("Hello, world!")
    
    encoding = detect_encoding(test_file_path)
    assert encoding.lower() == "utf-8"
    
    os.remove(test_file_path)

def test_split_text_into_chunks():
    test_file_path = "test_chunks.txt"
    with open(test_file_path, "w") as f:
        f.write("This is a test sentence. " * 100) # Create a long string
    
    chunks = split_text_into_chunks(test_file_path, 'utf-8', chunk_size=10)
    assert len(chunks) > 1
    assert len(chunks[0].split()) <= 10
    
    os.remove(test_file_path)

def test_delete_files():
    file1 = "temp_file1.txt"
    file2 = "temp_file2.txt"
    with open(file1, "w") as f: pass
    with open(file2, "w") as f: pass

    delete_files([file1, file2])
    assert not os.path.exists(file1)
    assert not os.path.exists(file2)

def test_extract_text_from_srt():
    srt_content = """
1
00:00:01,000 --> 00:00:03,000
Hello, world!

2
00:00:04,000 --> 00:00:06,000
(Sound of rain)
This is a test.

3
00:00:07,000 --> 00:00:09,000
SPEAKER: Another line.
"""
    test_srt_path = "test.srt"
    with open(test_srt_path, "w", encoding="utf-8") as f:
        f.write(srt_content)
    
    dialogues = extract_text_from_srt(test_srt_path, 'utf-8')
    assert "Hello, world!" in dialogues
    assert "This is a test." in dialogues
    assert "Another line." in dialogues
    assert "(Sound of rain)" not in dialogues # Parenthetical removed
    assert "SPEAKER:" not in dialogues # Speaker label removed
    
    os.remove(test_srt_path)

def test_process_srt():
    srt_content = """
1
00:00:01,000 --> 00:00:03,000
Hello, world!
"""
    input_file = "input.srt"
    output_file = "input_text.txt"
    with open(input_file, "w", encoding="utf-8") as f:
        f.write(srt_content)
    
    process_srt(input_file)
    assert os.path.exists(output_file)
    with open(output_file, "r", encoding="utf-8") as f:
        content = f.read()
        assert "Hello, world!" in content
    
    os.remove(input_file)
    os.remove(output_file)

def test_download_subs():
    # This test requires actual network access and a valid movie file.
    # For a unit test, you would typically mock the subliminal library calls.
    # Here's a conceptual example of how you might mock it:
    with patch('subliminal.scan_video') as mock_scan_video, \
         patch('subliminal.download_best_subtitles') as mock_download_best_subtitles, \
         patch('subliminal.save_subtitles') as mock_save_subtitles, \
         patch('pathlib.Path.stem', new_callable=PropertyMock) as mock_path_stem:
        
        mock_video = MagicMock()
        mock_scan_video.return_value = mock_video
        mock_download_best_subtitles.return_value = {mock_video: "mock_subtitle_data"}
        mock_path_stem.return_value = "mock_movie"

        # Create a dummy movie file for the function to scan
        dummy_movie_file = "dummy_movie.mp4"
        with open(dummy_movie_file, "w") as f:
            f.write("dummy content")

        download_subs(dummy_movie_file)
        
        mock_scan_video.assert_called_once_with(dummy_movie_file)
        mock_download_best_subtitles.assert_called_once()
        mock_save_subtitles.assert_called_once_with(mock_video, "mock_subtitle_data")
        
        os.remove(dummy_movie_file)