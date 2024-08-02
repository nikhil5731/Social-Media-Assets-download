from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yt_dlp
import asyncio
import concurrent.futures
import os

app = FastAPI()

# Allow CORS for all origins (not recommended for production)
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class VideoRequest(BaseModel):
    url: str


async def delete_file_after_delay(file_path: str, delay: int):
    await asyncio.sleep(delay)
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Deleted file: {file_path}")
    except PermissionError:
        loop = asyncio.get_event_loop()
        print("Trying to delete file due to Permission Error!")
        loop.create_task(delete_file_after_delay(file_path, delay=30))


@app.post("/download/")
async def download_video(video_request: VideoRequest):
    video_url = video_request.url
    if "youtube.com" not in video_url:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")

    ydl_opts = {
        "format": "bestvideo+bestaudio/best",  # Download best video and audio
        "outtmpl": "downloads/%(title)s.%(ext)s",
        "merge_output_format": "mp4",  # Ensure the final file is in mp4 format
    }

    def download():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            return ydl.prepare_filename(info_dict)

    try:
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            file_path = await loop.run_in_executor(pool, download)
            file_name = os.path.basename(file_path)

            loop.create_task(delete_file_after_delay(file_path, delay=30))

            return {"message": "Video downloaded successfully", "file_name": file_name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Serve the downloaded files
from fastapi.staticfiles import StaticFiles

app.mount("/downloads", StaticFiles(directory="downloads"), name="downloads")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
