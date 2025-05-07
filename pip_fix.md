# Fixing "pip command not found" Error

Here are simple solutions to fix the pip error:

## Method 1: Run pip through Python (Recommended)

Use this command instead:
```
python -m pip install -r requirements.txt
```

If that doesn't work, try:
```
py -m pip install -r requirements.txt
```

## Method 2: Add Python Scripts to PATH

1. Find your Python installation path:
   - Run `where python` in PowerShell to locate your Python executable
   - The Scripts folder will be in the same directory

2. Add to PATH:
   - Open Settings → System → About → Advanced System Settings
   - Click "Environment Variables"
   - Find "Path" in System variables, click Edit
   - Add the path to your Python Scripts folder (e.g., `C:\Users\YourUser\AppData\Local\Programs\Python\Python39\Scripts\`)
   - Click OK and close all windows
   - Restart PowerShell/Command Prompt

## Method 3: Install tkinter (if missing)

If you encounter tkinter errors after fixing pip:

```
python -m pip install tk
```

For additional audio processing dependencies:
```
python -m pip install numpy librosa scipy soundfile
``` 