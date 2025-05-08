# Voice Transformation API

This API transforms voice recordings to sound like old radio or walkie-talkie communications, with extensive customization options.

## Features

- **Old Radio Effect**: Simulates vintage AM radio with frequency limitations, distortion, noise, and vinyl dust effects
- **Walkie-Talkie Effect**: Recreates the compressed, limited sound of two-way radio communications
- **Graphical User Interface**: Simple GUI for easy testing and usage
- **REST API**: Complete API for integration with other services
- **Customizable Parameters**: Fine-tune every aspect of the audio transformation
- **URL or File Input**: Process audio from URLs or uploaded files
- **MP3 Output**: All processed audio is delivered in MP3 format

## Installation

1. Install the required dependencies:

```bash
pip install -r requirements.txt  # For desktop GUI
pip install -r requirements_api.txt  # For API server
```

2. Set up the dust effect for radio transformations:

```bash
python setup_dust_effect.py
```

## Usage

### Command Line Interface

Basic usage:

```bash
python voice_transformation.py input.wav output.wav
```

Specify the effect type (radio or walkie-talkie):

```bash
python voice_transformation.py input.wav output.wav --effect radio
python voice_transformation.py input.wav output.wav --effect walkie
```

### Graphical User Interface

For a more user-friendly experience, use the included GUI:

```bash
python voice_transformation_ui.py
```

### API Server

Start the API server:

```bash
python api_server.py
```

Access the API at `http://localhost:5555/docs`

## API Examples

### Transform audio from URL

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{
    "file_url": "https://example.com/audio.mp3",
    "effect": "radio",
    "style_params": {
      "distortion_amount": 1.3,
      "dust_level": 0.3
    }
  }' \
  http://localhost:5555/transform-url/
```

### Upload and transform audio

```bash
# Upload file
curl -X POST -F "file=@voice.wav" http://localhost:5555/upload/

# Transform with the returned file_id
curl -X POST -H "Content-Type: application/json" \
  -d '{
    "file_id": "returned_file_id",
    "effect": "walkie",
    "style_params": {
      "compression_ratio": 10.0
    }
  }' \
  http://localhost:5555/transform/
```

## Customization Options

### Radio Effect Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `distortion_amount` | Level of audio distortion | 1.2 |
| `noise_factor` | Amount of background noise | 0.008 |
| `low_cutoff` | Lower frequency cutoff (Hz) | 300 |
| `high_cutoff` | Upper frequency cutoff (Hz) | 3000 |
| `sample_rate` | Target sample rate for quality reduction | 8000 |
| `dust_level` | Level of vinyl dust/crackling effect | 0.2 |
| `use_dust_effect` | Enable/disable the dust effect | true |

### Walkie-Talkie Effect Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `distortion_amount` | Level of audio distortion | 1.05 |
| `noise_factor` | Amount of background noise | 0.01 |
| `low_cutoff` | Lower frequency cutoff (Hz) | 300 |
| `high_cutoff` | Upper frequency cutoff (Hz) | 4000 |
| `compression_ratio` | Dynamic range compression ratio | 8.0 |
| `attack_ms` | Compressor attack time (ms) | 5 |
| `release_ms` | Compressor release time (ms) | 150 |
| `bit_depth` | Bit depth for quality reduction | 8 |
| `static_level` | Amount of static effect | 0.03 |

## Response Format

API responses include:
- File ID
- Selected effect
- Applied style parameters
- Download URL
- Audio duration in seconds

Example:
```json
{
  "file_id": "abc123...",
  "effect": "radio",
  "status": "success",
  "style_params": {
    "distortion_amount": 1.3,
    "dust_level": 0.2
  },
  "duration_seconds": 15.6,
  "download_url": "/download/abc123_radio"
}
```

## Deployment

For production deployment instructions, see [deployment_guide.md](deployment_guide.md). 