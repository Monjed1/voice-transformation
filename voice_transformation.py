import numpy as np
import librosa
import librosa.display
import soundfile as sf
from scipy import signal
import argparse

def add_noise(audio, noise_factor=0.005):
    """Add background noise to the audio signal."""
    noise = np.random.normal(0, audio.std(), audio.shape) * noise_factor
    return audio + noise

def apply_bandpass_filter(audio, sr, low_cutoff=300, high_cutoff=3000):
    """Apply a bandpass filter to simulate limited frequency response."""
    nyquist = 0.5 * sr
    low = low_cutoff / nyquist
    high = high_cutoff / nyquist
    b, a = signal.butter(4, [low, high], btype='band')
    return signal.filtfilt(b, a, audio)

def apply_highpass_filter(audio, sr, cutoff=300):
    """Apply a high-pass filter to remove bass frequencies."""
    nyquist = 0.5 * sr
    normalized_cutoff = cutoff / nyquist
    b, a = signal.butter(4, normalized_cutoff, btype='high')
    return signal.filtfilt(b, a, audio)

def apply_lowpass_filter(audio, sr, cutoff=4000):
    """Apply a low-pass filter to limit high-frequency detail."""
    nyquist = 0.5 * sr
    normalized_cutoff = cutoff / nyquist
    b, a = signal.butter(4, normalized_cutoff, btype='low')
    return signal.filtfilt(b, a, audio)

def apply_distortion(audio, amount=2.0):
    """Apply distortion to the audio signal."""
    return np.clip(audio * amount, -1, 1)

def apply_bit_crusher(audio, bits=8):
    """Simulate bit-depth reduction for lo-fi effect."""
    # Calculate the number of possible values
    max_val = 2**(bits-1)
    # Quantize the signal (multiply, round, divide)
    return np.round(audio * max_val) / max_val

def add_static_effect(audio, static_level=0.01, static_freq=0.1):
    """Add intermittent static noise effect."""
    static = np.random.normal(0, 1, audio.shape) * static_level
    # Create an envelope for the static to make it intermittent
    t = np.linspace(0, 1, len(audio))
    envelope = 0.5 * (1 + np.sin(2 * np.pi * static_freq * t))
    envelope = envelope.reshape(-1, 1) if audio.ndim > 1 else envelope
    return audio + static * envelope

def reduce_sample_rate(audio, original_sr, target_sr):
    """Reduce sample rate to simulate low-quality audio."""
    # Resample to lower rate
    resampled = librosa.resample(audio, orig_sr=original_sr, target_sr=target_sr)
    # Then resample back to original rate (this maintains the reduced quality)
    return librosa.resample(resampled, orig_sr=target_sr, target_sr=original_sr)

def apply_compression(audio, threshold=0.3, ratio=8.0, attack_ms=5, release_ms=150):
    """Apply dynamic range compression to the audio."""
    # Convert attack and release from ms to samples
    sr = 22050  # Default sample rate in librosa
    attack = int(sr * attack_ms / 1000)
    release = int(sr * release_ms / 1000)
    
    # Initialize gain envelope
    gain_envelope = np.ones_like(audio)
    
    # Calculate the amount of gain reduction needed at each sample
    for i in range(len(audio)):
        # Determine the level
        level = abs(audio[i])
        
        # If level is above threshold, calculate gain reduction
        if level > threshold:
            gain_reduction = ((level - threshold) * (1 - 1/ratio)) / level
            
            # Apply attack and release
            if i > 0:
                # Rate of attack or release
                if gain_reduction > gain_envelope[i-1]:
                    # Attack (faster gain reduction)
                    gain_envelope[i] = min(gain_envelope[i-1] + (1 - gain_envelope[i-1]) / attack, 1 - gain_reduction)
                else:
                    # Release (slower gain recovery)
                    gain_envelope[i] = max(gain_envelope[i-1] - gain_envelope[i-1] / release, 1 - gain_reduction)
            else:
                gain_envelope[i] = 1 - gain_reduction
    
    # Apply the gain envelope
    compressed_audio = audio * gain_envelope
    
    # Apply makeup gain to normalize the output
    if np.max(np.abs(compressed_audio)) > 0:
        makeup_gain = min(0.95 / np.max(np.abs(compressed_audio)), 2.0)  # limit to 2x gain
        compressed_audio = compressed_audio * makeup_gain
    
    return compressed_audio

def add_ptt_artifacts(audio, sr):
    """Add push-to-talk button click artifacts at the beginning and end."""
    # Define duration of click in seconds
    click_duration = 0.03  # 30ms
    
    # Number of samples for click
    num_click_samples = int(click_duration * sr)
    
    # Create a click/pop sound using filtered noise
    click = np.random.normal(0, 1, num_click_samples)
    
    # Apply bandpass filter to the click
    nyquist = 0.5 * sr
    low, high = 800 / nyquist, 3000 / nyquist
    b, a = signal.butter(2, [low, high], btype='band')
    click = signal.filtfilt(b, a, click)
    
    # Apply envelope to the click
    env = np.exp(-np.linspace(0, 5, num_click_samples))
    click = click * env * 0.2  # Scale down to avoid excessive volume
    
    # Add reversed click at the end
    end_click = click[::-1] * 0.15  # Slightly quieter end click
    
    # Create new audio with clicks at beginning and end
    result = np.zeros(len(audio) + 2 * num_click_samples)
    result[:num_click_samples] = click
    result[num_click_samples:num_click_samples+len(audio)] = audio
    result[num_click_samples+len(audio):] = end_click
    
    return result

def mix_with_background(audio, background_audio, background_level=0.2):
    """Mix the processed audio with a background effect like dust or static."""
    # Make sure the background audio is the same length as the main audio
    if len(background_audio) < len(audio):
        # If background is shorter, loop it to match the length of the main audio
        repetitions = int(np.ceil(len(audio) / len(background_audio)))
        background_audio = np.tile(background_audio, repetitions)
        # Trim to match exactly
        background_audio = background_audio[:len(audio)]
    elif len(background_audio) > len(audio):
        # If background is longer, trim it
        background_audio = background_audio[:len(audio)]
    
    # Mix the audio with the background
    mixed_audio = audio + (background_audio * background_level)
    
    # Normalize to avoid clipping
    if np.max(np.abs(mixed_audio)) > 1.0:
        mixed_audio = mixed_audio / np.max(np.abs(mixed_audio)) * 0.95
    
    return mixed_audio

def simulate_old_radio(audio, sr, **style_params):
    """Apply effects to simulate an old radio."""
    # Get style parameters or use defaults
    low_cutoff = style_params.get('low_cutoff', 300)
    high_cutoff = style_params.get('high_cutoff', 3000)
    distortion_amount = style_params.get('distortion_amount', 1.2)
    noise_factor = style_params.get('noise_factor', 0.008)
    target_sample_rate = style_params.get('sample_rate', 8000)
    dust_level = style_params.get('dust_level', 0.2)
    use_dust_effect = style_params.get('use_dust_effect', True)
    
    # Apply bandpass filter to limit frequency range
    audio = apply_bandpass_filter(audio, sr, low_cutoff=low_cutoff, high_cutoff=high_cutoff)
    
    # Add minimal distortion
    audio = apply_distortion(audio, amount=distortion_amount)
    
    # Add slight noise (AM radio hiss)
    audio = add_noise(audio, noise_factor=noise_factor)
    
    # Reduce sample rate to simulate low-quality audio
    if target_sample_rate and target_sample_rate < sr:
        audio = reduce_sample_rate(audio, sr, target_sample_rate)
    
    # Add dust effect if enabled
    if use_dust_effect:
        try:
            import os
            # Create resources directory if it doesn't exist
            if not os.path.exists('resources'):
                os.makedirs('resources')
                
            dust_path = 'resources/dusteffect.wav'
            if os.path.exists(dust_path):
                # Load the dust effect
                dust_effect, dust_sr = librosa.load(dust_path, sr=sr)
                # Mix with the processed audio
                audio = mix_with_background(audio, dust_effect, dust_level)
                print(f"Added dust effect at level {dust_level}")
            else:
                print(f"Warning: Dust effect file not found at {dust_path}")
        except Exception as e:
            print(f"Error adding dust effect: {str(e)}")
    
    return audio

def simulate_walkie_talkie(audio, sr, **style_params):
    """Apply effects to simulate a walkie-talkie using professional-grade processing."""
    # Get style parameters or use defaults
    low_cutoff = style_params.get('low_cutoff', 300)
    high_cutoff = style_params.get('high_cutoff', 4000)
    distortion_amount = style_params.get('distortion_amount', 1.05)
    noise_factor = style_params.get('noise_factor', 0.01)
    static_level = style_params.get('static_level', 0.03)
    compression_ratio = style_params.get('compression_ratio', 8.0)
    attack_ms = style_params.get('attack_ms', 5)
    release_ms = style_params.get('release_ms', 150)
    bit_depth = style_params.get('bit_depth', 8)
    
    # 1. Apply high-pass filter (remove bass frequencies below 300 Hz)
    audio = apply_highpass_filter(audio, sr, cutoff=low_cutoff)
    
    # 2. Apply low-pass filter (limit high frequencies above 4 kHz)
    audio = apply_lowpass_filter(audio, sr, cutoff=high_cutoff)
    
    # 3. Apply compression (narrow dynamic range, 8:1 ratio)
    audio = apply_compression(audio, threshold=0.3, ratio=compression_ratio, 
                             attack_ms=attack_ms, release_ms=release_ms)
    
    # 4. Add minimal distortion and bit crushing (simulate 8-bit audio)
    audio = apply_distortion(audio, amount=distortion_amount)
    audio = apply_bit_crusher(audio, bits=bit_depth)
    
    # 5. Add push-to-talk artifacts (clicks at start and end)
    audio = add_ptt_artifacts(audio, sr)
    
    # 6. Add background noise and static
    audio = add_noise(audio, noise_factor=noise_factor)
    audio = add_static_effect(audio, static_level=static_level, static_freq=0.3)
    
    return audio

def process_audio(input_file, output_file, effect_type, **style_params):
    """Load audio, apply the chosen effect, and save the result."""
    print(f"Loading audio file: {input_file}")
    audio, sr = librosa.load(input_file, sr=None)
    
    print(f"Applying {effect_type} effect with custom style params: {style_params}")
    if effect_type == 'radio':
        processed_audio = simulate_old_radio(audio, sr, **style_params)
    elif effect_type == 'walkie':
        processed_audio = simulate_walkie_talkie(audio, sr, **style_params)
    else:
        raise ValueError("Effect type must be 'radio' or 'walkie'")
    
    print(f"Saving processed audio to: {output_file}")
    sf.write(output_file, processed_audio, sr)
    print("Done!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Transform voice recordings to sound like old radio or walkie-talkie.')
    parser.add_argument('input_file', help='Path to the input audio file')
    parser.add_argument('output_file', help='Path where the processed audio will be saved')
    parser.add_argument('--effect', choices=['radio', 'walkie'], default='radio',
                        help='The effect to apply: "radio" for old radio or "walkie" for walkie-talkie (default: radio)')
    
    args = parser.parse_args()
    process_audio(args.input_file, args.output_file, args.effect) 