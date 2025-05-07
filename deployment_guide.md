# Voice Transformation API Deployment Guide

This guide will help you deploy the Voice Transformation API to a VPS (Virtual Private Server).

## Prerequisites

- A VPS with Ubuntu 20.04 or newer
- SSH access to your VPS
- Domain name (optional but recommended)

## Server Setup

1. **Connect to your VPS via SSH**

```bash
ssh username@your_server_ip
```

2. **Update system packages**

```bash
sudo apt update && sudo apt upgrade -y
```

3. **Install required dependencies**

```bash
sudo apt install -y python3 python3-pip python3-dev nginx supervisor git ffmpeg
```

## Deploying the Application

1. **Clone the repository (or upload your files)**

```bash
git clone https://github.com/yourusername/voice-transformation.git
cd voice-transformation
```

2. **Install Python dependencies**

```bash
pip3 install -r requirements_api.txt
```

3. **Test the application**

```bash
python3 api_server.py
```

Visit `http://your_server_ip:5555/docs` to see if the API documentation loads.

## Production Setup with Supervisor

1. **Create a Supervisor configuration file**

```bash
sudo nano /etc/supervisor/conf.d/voice-transformation.conf
```

2. **Add the following configuration**

```ini
[program:voice-transformation]
directory=/path/to/voice-transformation
command=python3 -m uvicorn api_server:app --host 0.0.0.0 --port 5555
autostart=true
autorestart=true
stderr_logfile=/var/log/voice-transformation.err.log
stdout_logfile=/var/log/voice-transformation.out.log
user=your_username
```

3. **Update Supervisor**

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl restart voice-transformation
```

## Setting up Nginx as a Reverse Proxy

1. **Create an Nginx configuration file**

```bash
sudo nano /etc/nginx/sites-available/voice-transformation
```

2. **Add the following configuration**

```nginx
server {
    listen 80;
    server_name your_domain.com;  # or your server IP if no domain

    location / {
        proxy_pass http://127.0.0.1:5555;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Increase timeout for audio processing
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }

    # Increase client max body size for larger audio files
    client_max_body_size 50M;
}
```

3. **Enable the site and restart Nginx**

```bash
sudo ln -s /etc/nginx/sites-available/voice-transformation /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Security Recommendations

1. **Set up a firewall**

```bash
sudo apt install -y ufw
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

2. **Set up SSL with Certbot**

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your_domain.com
```

3. **Add API authentication**

Edit `api_server.py` to add bearer token or OAuth2 authentication.

## Using the API

Once deployed, you can use the API with the following methods:

### Method 1: Using a Direct URL to the Audio File

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{
    "file_url": "https://example.com/path/to/audio.mp3",
    "effect": "radio",
    "style_params": {
      "distortion_amount": 1.3,
      "noise_factor": 0.01,
      "low_cutoff": 250,
      "high_cutoff": 3500
    }
  }' \
  https://your_domain.com/transform-url/
```

This will download the audio from the provided URL, apply the transformation with custom parameters, and return a link to download the MP3 file.

### Method 2: Uploading a File First

1. **Upload an audio file**

```bash
curl -X POST -F "file=@your_audio.wav" https://your_domain.com/upload/
```

2. **Transform the file with custom parameters**

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{
    "file_id": "the_returned_file_id",
    "effect": "walkie",
    "style_params": {
      "compression_ratio": 10.0,
      "distortion_amount": 1.1,
      "bit_depth": 10
    }
  }' \
  https://your_domain.com/transform/
```

3. **Download the processed file**

```bash
curl -X GET https://your_domain.com/download/the_returned_file_id_walkie -o processed_audio.mp3
```

## Customizable Style Parameters

You can customize the voice transformation by providing `style_params` in your API request:

### Common Parameters (for both effects)

- `noise_factor`: Amount of background noise (default: 0.008 for radio, 0.01 for walkie)
- `distortion_amount`: Level of distortion effect (default: 1.2 for radio, 1.05 for walkie)

### Radio-Specific Parameters

- `low_cutoff`: Lower frequency cutoff in Hz (default: 300)
- `high_cutoff`: Upper frequency cutoff in Hz (default: 3000)
- `sample_rate`: Target sample rate for quality reduction (default: 8000)

### Walkie-Talkie Specific Parameters

- `low_cutoff`: Lower frequency cutoff in Hz (default: 300)
- `high_cutoff`: Upper frequency cutoff in Hz (default: 4000)
- `compression_ratio`: Dynamic range compression ratio (default: 8.0)
- `attack_ms`: Compressor attack time in milliseconds (default: 5)
- `release_ms`: Compressor release time in milliseconds (default: 150)
- `bit_depth`: Bit depth for quality reduction (default: 8)
- `static_level`: Amount of static effect (default: 0.03)

## API Response Format

When you call the transformation endpoint, you'll receive a JSON response like:

```json
{
  "file_id": "abc123...",
  "effect": "radio",
  "status": "success",
  "style_params": {
    "distortion_amount": 1.3,
    "noise_factor": 0.01
  },
  "download_url": "/download/abc123_radio"
}
```

The `download_url` field contains the path to download the processed MP3 file.

## Monitoring and Maintenance

- Check logs: `sudo tail -f /var/log/voice-transformation.out.log`
- Restart the application: `sudo supervisorctl restart voice-transformation`
- Check Nginx status: `sudo systemctl status nginx` 