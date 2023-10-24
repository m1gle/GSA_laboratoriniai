import matplotlib.pyplot as plt
import wave
import os
from tkinter import filedialog
import numpy as np

def openFile():
    file = filedialog.askopenfilename(filetypes=[('sound','*.wav')])
    return file

def readFile(file):
    sound = wave.open(file, 'rb')
    channels = sound.getnchannels() # kanalų skaičius
    sampWidth = sound.getsampwidth() * 8 # baitus dauginame iš 8, kad gautume bitus
    frameRate = sound.getframerate() # garso dažnis (Hz)
    numFrames = sound.getnframes() # garso kadrų skaičius 
    frames = sound.readframes(numFrames)
    duration = numFrames / frameRate
    fileName = os.path.basename(file)

    sound.close()

    return (channels, sampWidth, frameRate, numFrames, duration, fileName, frames)

def calculateAmplitude(sampWidth): # paverčiame amplitudę realia (iš [-1; 1], į )
    maxAmplitude = 2 ** (sampWidth - 1) - 1
    minAmplitude = -2 ** (sampWidth - 1)
    return (maxAmplitude, minAmplitude)

def applyEchoEffect(frames, frameRate, channels, sampWidth, fileName):
    soundSignal = np.frombuffer(frames, dtype=np.int16)
    # aspkaičiuojamas Δ (suvėlinimas)
    delaySamples = int(echo * frameRate)
    # sukuriamas pavėlintas signalas
    delaySignal = np.zeros_like(soundSignal)
    delaySignal[delaySamples:] = soundSignal[:-delaySamples]

    # uždedamas aido efektas
    processedSignal = soundSignal + delay * delaySignal

    # įsitikiname, kad signalas [-32768, 32767] režiuose, kad nebūtų "ausims skaudžių" garso šuolių
    processedSignal = np.clip(processedSignal, -32768, 32767)

    # išsaugomas garso failas
    out_file = fileName + "_echo.wav"
    out_sound = wave.open(out_file, 'wb')
    out_sound.setnchannels(channels)
    out_sound.setsampwidth(int(sampWidth / 8))
    out_sound.setframerate(frameRate)
    out_sound.writeframes(processedSignal.astype(np.int16).tobytes())
    out_sound.close()
    return (delaySignal)

def drawGraphs (duration, channels, maxAmplitude, minAmplitude, numFrames, samples, delaySignal):
    xAxis = np.linspace(0, duration, numFrames)
    delayScale = 0.8
    
    if channels == 1:
        plt.grid(True)
        plt.plot(xAxis, samples)
        plt.plot(xAxis, delaySignal * delayScale)
        plt.title("Kanalų skaičius - 1 (mono)")
        plt.xlabel('Laikas (s)')
        plt.ylabel('Amplitudė')
        plt.ylim(minAmplitude, maxAmplitude)

    elif channels == 2:
        left_channel_samples = samples[::2]
        right_channel_samples = samples[1::2]
        left_channel_delay = samples[::2]
        right_channel_delay = samples[1::2]
        
        plt.subplot(2, 1, 1)
        plt.grid(True)
        plt.plot(xAxis, left_channel_samples)
        plt.plot(xAxis, left_channel_delay * delayScale)
        plt.title("Kanalų skaičius - 2 (stereo) pirmas kanalas")
        plt.xlabel('Laikas (s)')
        plt.ylabel('Amplitudė')
        plt.ylim(minAmplitude, maxAmplitude)

        plt.subplot(2, 1, 2)
        plt.grid(True)
        plt.plot(xAxis, right_channel_samples)
        plt.plot(xAxis, right_channel_delay * delayScale)
        plt.title("Kanalų skaičius - 2 (stereo) antras kanalas")
        plt.xlabel('Laikas (s)')
        plt.ylabel('Amplitudė')
        plt.ylim(minAmplitude, maxAmplitude)

    plt.tight_layout(pad=1)
    plt.show()

def printInfo(channels, duration, sampWidth, fileName, minAmplitude, maxAmplitude):
    x = 5
    if (channels == 1):
        channelsText = 'mono'
    else:
        channelsText = 'stereo'

    result = (
        f'Failo pavadinimas - {fileName}\n'
        f'Kanalų skaičius - {channels} ({channelsText})\n'
        f'Diskretizavimo dažnis - {round(duration, 3)} s\n'
        f'Kvantavimo gylis - {sampWidth} bitų\n'
        f'Signalo amplitudė (reali) - [{minAmplitude}; {maxAmplitude}]')
    print(result)

# Aido parametrai
echo = 0.2 # formulėje - α
delay = 0.6 # formulėje - Δ

file = openFile()

channels, sampWidth, frameRate, numFrames, duration, fileName, frames = readFile(file)
delaySignal = applyEchoEffect(frames, frameRate, channels, sampWidth, fileName)
samples = np.frombuffer(frames, np.int16)
maxAmplitude, minAmplitude = calculateAmplitude(sampWidth)

drawGraphs(duration, channels, maxAmplitude, minAmplitude, numFrames, samples, delaySignal)
printInfo(channels, duration, sampWidth, fileName, minAmplitude, maxAmplitude)
