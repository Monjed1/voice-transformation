from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, HttpUrl
import uvicorn
import os
import uuid
import shutil
import requests
from typing import Optional, Union, Dict, Any
from voice_transformation import process_audio
from pydub import AudioSegment

app = FastAPI(
    title="Voice Transformation API",
    description="API for transforming voice recordings to sound like old radio or walkie-talkie",
    version="1.0.0"
)

# Create uploads and results directories if they don't exist
os.makedirs("uploads", exist_ok=True)
os.makedirs("results", exist_ok=True)

class StyleParams(BaseModel):
    # Common parameters
    noise_factor: Optional[float] = None
    distortion_amount: Optional[float] = None
    
    # Radio-specific parameters
    low_cutoff: Optional[int] = None
    high_cutoff: Optional[int] = None
    sample_rate: Optional[int] = None
    
    # Walkie-talkie specific parameters
    compression_ratio: Optional[float] = None
    attack_ms: Optional[int] = None
    release_ms: Optional[int] = None
    bit_depth: Optional[int] = None
    static_level: Optional[float] = None

class TransformationRequest(BaseModel):
    effect: str = "radio"
    file_id: Optional[str] = None
    file_url: Optional[HttpUrl] = None
    style_params: Optional[StyleParams] = None

class UrlTransformationRequest(BaseModel):
    effect: str = "radio"
    file_url: HttpUrl
    style_params: Optional[StyleParams] = None

@app.get("/")
async def root():
    return {"message": "Voice Transformation API is running"}

@app.post("/upload/")
async def upload_audio(file: UploadFile = File(...)):
    """
    Upload an audio file for transformation
    """
    if not file.filename.lower().endswith(('.wav', '.mp3', '.ogg', '.flac')):
        raise HTTPException(status_code=400, detail="Unsupported file format. Please upload .wav, .mp3, .ogg, or .flac files")
    
    # Generate a unique file ID and save the uploaded file
    file_id = str(uuid.uuid4())
    file_extension = os.path.splitext(file.filename)[1]
    file_path = f"uploads/{file_id}{file_extension}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return {"file_id": file_id, "original_filename": file.filename}

@app.post("/transform-url/")
async def transform_url(request: UrlTransformationRequest, background_tasks: BackgroundTasks):
    """
    Download and transform an audio file from a URL
    """
    if request.effect not in ["radio", "walkie"]:
        raise HTTPException(status_code=400, detail="Effect must be 'radio' or 'walkie'")
    
    # Generate a unique ID for this request
    file_id = str(uuid.uuid4())
    
    try:
        # Download the file from URL
        response = requests.get(str(request.file_url), stream=True)
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail=f"Failed to download from URL: {response.status_code}")
        
        # Determine file extension from URL or content type
        content_type = response.headers.get('content-type', '')
        if 'audio/mpeg' in content_type or 'audio/mp3' in content_type:
            extension = '.mp3'
        elif 'audio/wav' in content_type:
            extension = '.wav'
        elif 'audio/ogg' in content_type:
            extension = '.ogg'
        elif 'audio/flac' in content_type:
            extension = '.flac'
        else:
            # Try to get extension from URL
            url_path = str(request.file_url).split('?')[0]  # Remove query params
            if url_path.endswith(('.mp3', '.wav', '.ogg', '.flac')):
                extension = os.path.splitext(url_path)[1]
            else:
                extension = '.mp3'  # Default to mp3
        
        input_file = f"uploads/{file_id}{extension}"
        
        # Save the downloaded file
        with open(input_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        # Process the audio
        wav_output = f"results/{file_id}_{request.effect}.wav"
        mp3_output = f"results/{file_id}_{request.effect}.mp3"
        
        # Extract style parameters if provided
        style_params = {}
        if request.style_params:
            style_params = request.style_params.dict(exclude_none=True)
        
        # Process audio with style parameters
        process_audio(input_file, wav_output, request.effect, **style_params)
        
        # Convert WAV to MP3
        convert_to_mp3(wav_output, mp3_output)
        
        # Remove temporary WAV file
        if os.path.exists(wav_output):
            os.remove(wav_output)
        
        # Schedule cleanup
        background_tasks.add_task(schedule_cleanup, input_file, mp3_output)
        
        # Generate a download URL
        download_url = f"/download/{file_id}_{request.effect}"
        
        return {
            "file_id": file_id,
            "effect": request.effect,
            "status": "success",
            "style_params": style_params,
            "download_url": download_url
        }
        
    except Exception as e:
        # Clean up any partial files
        for file_path in [f"uploads/{file_id}{ext}" for ext in ['.mp3', '.wav', '.ogg', '.flac']]:
            if os.path.exists(file_path):
                os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Error processing audio: {str(e)}")

@app.post("/transform/")
async def transform_audio(request: TransformationRequest, background_tasks: BackgroundTasks):
    """
    Transform an uploaded audio file with the specified effect
    """
    # Check if we have a URL or file_id
    if request.file_url and not request.file_id:
        # If URL is provided, redirect to transform_url
        url_request = UrlTransformationRequest(
            effect=request.effect, 
            file_url=request.file_url,
            style_params=request.style_params
        )
        return await transform_url(url_request, background_tasks)
    
    if not request.file_id:
        raise HTTPException(status_code=400, detail="Either file_id or file_url must be provided")
        
    # Find the uploaded file
    uploaded_files = [f for f in os.listdir("uploads") if f.startswith(request.file_id)]
    if not uploaded_files:
        raise HTTPException(status_code=404, detail=f"File with ID {request.file_id} not found")
    
    input_file = os.path.join("uploads", uploaded_files[0])
    wav_output = f"results/{request.file_id}_{request.effect}.wav"
    mp3_output = f"results/{request.file_id}_{request.effect}.mp3"
    
    # Validate effect type
    if request.effect not in ["radio", "walkie"]:
        raise HTTPException(status_code=400, detail="Effect must be 'radio' or 'walkie'")
    
    try:
        # Extract style parameters if provided
        style_params = {}
        if request.style_params:
            style_params = request.style_params.dict(exclude_none=True)
            
        # Process the audio with style parameters
        process_audio(input_file, wav_output, request.effect, **style_params)
        
        # Convert WAV to MP3
        convert_to_mp3(wav_output, mp3_output)
        
        # Remove temporary WAV file
        if os.path.exists(wav_output):
            os.remove(wav_output)
        
        # Schedule file cleanup (delete after 1 hour)
        background_tasks.add_task(schedule_cleanup, input_file, mp3_output)
        
        return {
            "file_id": request.file_id,
            "effect": request.effect,
            "status": "success",
            "style_params": style_params,
            "download_url": f"/download/{request.file_id}_{request.effect}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing audio: {str(e)}")

@app.get("/download/{file_name}")
async def download_file(file_name: str):
    """
    Download a transformed audio file in MP3 format
    """
    file_path = f"results/{file_name}.mp3"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(file_path, media_type="audio/mpeg", filename=f"{file_name}.mp3")

def convert_to_mp3(wav_file, mp3_file):
    """Convert WAV file to MP3 format"""
    try:
        audio = AudioSegment.from_wav(wav_file)
        audio.export(mp3_file, format="mp3")
    except Exception as e:
        raise Exception(f"Failed to convert to MP3: {str(e)}")

def schedule_cleanup(input_file: str, output_file: str, delay_hours: int = 1):
    """
    Schedule cleanup of files after a delay
    Note: In a production environment, you would use a proper task queue like Celery
    """
    import time
    import threading
    
    def delete_files():
        time.sleep(delay_hours * 3600)  # Convert hours to seconds
        try:
            if os.path.exists(input_file):
                os.remove(input_file)
            if os.path.exists(output_file):
                os.remove(output_file)
        except Exception:
            pass
    
    thread = threading.Thread(target=delete_files)
    thread.daemon = True
    thread.start()

if __name__ == "__main__":
    uvicorn.run("api_server:app", host="0.0.0.0", port=5555, reload=True) 