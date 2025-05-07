# Voice Transformation Script

This Python script transforms voice recordings to sound like old radio or walkie-talkie.

## Features

- **Old Radio Effect**: Applies bandpass filtering, distortion, and static noise to simulate vintage radio sound
- **Walkie-Talkie Effect**: Creates a more compressed sound with characteristic static bursts
- **Graphical User Interface**: Simple GUI for easy testing and usage

## Installation

1. Install the required dependencies:

```bash
pip install -r requirements.txt
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

For a more user-friendly experience, you can use the included GUI:

```bash
python voice_transformation_ui.py
```

With the GUI, you can:
- Select input and output files using file dialogs
- Choose between radio and walkie-talkie effects
- Process audio with a single click
- Monitor the progress with visual feedback

## Supported Audio Formats

The script supports various audio formats including WAV, MP3, FLAC, and OGG, depending on the capabilities of the installed version of librosa and soundfile.

## Example

Transform a voice recording to sound like an old radio:

```bash
python voice_transformation.py my_voice.wav radio_voice.wav --effect radio
``` 