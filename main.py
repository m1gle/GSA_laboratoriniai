import matplotlib.pyplot as plt
import wave
import os
from tkinter import filedialog
import matplotlib.pyplot as plt
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

def calculateAmplitude(sampWidth): # paverčiame amplitudę realia (iš [-1; 1])
    maxAmplitude = 2 ** (sampWidth - 1) - 1
    minAmplitude = -2 ** (sampWidth - 1)
    return (maxAmplitude, minAmplitude)

def getMarker(duration):
    text = "Įveskite laiko žymeklį, kuris nėra didesnis nei " + str(round(duration, 3)) + " s: "
    marker = float(input(text))
    return (marker)

def drawGraphs (duration, channels, maxAmplitude, minAmplitude, marker, numFrames, samples):
    xAxis = np.linspace(0, duration, numFrames)

    if channels == 1:
        plt.grid(True)
        plt.plot(xAxis, samples, color='lightgreen')
        plt.title("Kanalų skaičius - 1 (mono)")
        plt.xlabel('Laikas (s)')
        plt.ylabel('Amplitudė')
        plt.ylim(minAmplitude, maxAmplitude)
        plt.axvline(x=marker, color='crimson')

    elif channels == 2:
        left_channel = samples[::2]
        right_channel = samples[1::2]
        
        plt.subplot(2, 1, 1)
        plt.grid(True)
        plt.plot(xAxis, left_channel, color='turquoise')
        plt.title("Kanalų skaičius - 2 (stereo) pirmas kanalas")
        plt.xlabel('Laikas (s)')
        plt.ylabel('Amplitudė')
        plt.ylim(minAmplitude, maxAmplitude)
        plt.axvline(x=marker, color='crimson')

        plt.subplot(2, 1, 2)
        plt.grid(True)
        plt.plot(xAxis, right_channel, color='coral')
        plt.title("Kanalų skaičius - 2 (stereo) antras kanalas")
        plt.xlabel('Laikas (s)')
        plt.ylabel('Amplitudė')
        plt.ylim(minAmplitude, maxAmplitude)
        plt.axvline(x=marker, color='crimson')

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



file = openFile()
channels, sampWidth, frameRate, numFrames, duration, fileName, frames = readFile(file)
maxAmplitude, minAmplitude = calculateAmplitude(sampWidth)
marker = getMarker(duration)
samples = np.frombuffer(frames, np.int16)
drawGraphs(duration, channels, maxAmplitude, minAmplitude, marker, numFrames, samples)
printInfo(channels, duration, sampWidth, fileName, minAmplitude, maxAmplitude)