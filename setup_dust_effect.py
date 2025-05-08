#!/usr/bin/env python3
"""
Setup script to check for the dust effect resource file.
If the file is missing, it creates a simple placeholder.
"""

import os
import numpy as np
import soundfile as sf

def create_dust_effect(duration_seconds=5.0, sample_rate=22050):
    """Create a simple dust effect if one doesn't exist."""
    # Create a resources directory if it doesn't exist
    if not os.path.exists('resources'):
        print("Creating resources directory...")
        os.makedirs('resources')
    
    dust_path = 'resources/dusteffect.wav'
    
    # Only create the file if it doesn't exist
    if not os.path.exists(dust_path):
        print(f"Dust effect file not found at {dust_path}. Creating a placeholder...")
        
        # Generate a simple noise-based dust effect
        # This is just a placeholder - users should replace with a better dust effect
        num_samples = int(duration_seconds * sample_rate)
        
        # Generate filtered noise for dust effect
        noise = np.random.normal(0, 0.1, num_samples)
        
        # Apply envelope to make it sound more like dust/crackle
        t = np.linspace(0, duration_seconds, num_samples)
        
        # Create random positions for dust crackles
        crackle_positions = np.random.random(100) * duration_seconds
        crackle_amplitudes = np.random.random(100) * 0.4 + 0.1
        
        # Add individual crackles
        crackle = np.zeros(num_samples)
        for pos, amp in zip(crackle_positions, crackle_amplitudes):
            # Find the nearest index
            idx = int(pos * sample_rate)
            if idx < num_samples - 10:
                # Add a short impulse
                crackle[idx:idx+10] += np.random.random(10) * amp * np.exp(-np.arange(10)/2)
        
        # Mix the continuous noise with the crackles
        dust_effect = noise * 0.3 + crackle
        
        # Normalize
        dust_effect = dust_effect / np.max(np.abs(dust_effect)) * 0.8
        
        # Save the dust effect
        sf.write(dust_path, dust_effect, sample_rate)
        print(f"Created placeholder dust effect at {dust_path}")
        print("Note: This is a computer-generated placeholder. For better results,")
        print("      replace this file with a real vinyl record dust/static recording.")
    else:
        print(f"Found existing dust effect at {dust_path}")

if __name__ == "__main__":
    create_dust_effect()
    print("\nSetup complete. You can now use the dust effect with the radio transformation.")
    print("To adjust the level of the effect, use the 'dust_level' parameter (default: 0.2)")
    print("Example API call:")
    print("""
    {
      "file_url": "https://example.com/audio.mp3",
      "effect": "radio",
      "style_params": {
        "dust_level": 0.3,
        "use_dust_effect": true
      }
    }
    """) 