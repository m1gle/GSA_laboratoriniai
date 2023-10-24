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

def calculateAmplitude(sampWidth): # paverčiame amplitudę realia (iš [-1; 1])
    maxAmplitude = 2 ** (sampWidth - 1) - 1
    minAmplitude = -2 ** (sampWidth - 1)
    return (maxAmplitude, minAmplitude)

def calculateEnergy(data, frameLength, hopLength): 
    energy = [] 
    dataLength = len(data) 
    for i in range(hopLength, dataLength - frameLength, hopLength): 
        currentFrame = np.sum(data[i:i + frameLength] ** 2) / frameLength 
        energy.append(currentFrame) 
    return energy 

def s(value):  
    if value >= 0: 
        return 1 
    return -1 

def calculateZRC(samples, frameLength):
    ZRC = []
    dataLength = len(samples) 
    for i in range(0, dataLength, frameLength): 
        currentFrame = 0 
        for j in range(i, i + frameLength): 
            if (j < dataLength): 
                currentFrame += abs(s(samples[j]) - s(samples[j - 1])) 
        ZRC.append(currentFrame / (2*frameLength)) 
    return ZRC

def segment_signal(energy, threshold):
    segments = []
    segment_start = 0
    in_segment = False

    for i, energy_value in enumerate(energy):
        if energy_value > threshold:
            if not in_segment:
                segment_start = i
                in_segment = True
        else:
            if in_segment:
                segments.append((segment_start, i))
                in_segment = False

    return segments

def drawGraph(fileName, title, duration, yAxis, xlabel, ylabel):
    xAxis = np.linspace(0, duration, num=len(yAxis)) # gaunama x ašis - laiko
    plt.plot(xAxis, yAxis) 
    plt.title(fileName + " " + title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid()
    plt.show()

def detectSegments(energy, threshold):
    segments = []
    segment_start = 0
    in_segment = False

    for i, energy_value in enumerate(energy):
        if energy_value > threshold:
            if not in_segment:
                segment_start = i
                in_segment = True
        else:
            if in_segment:
                segment_end = i
                segments.append((segment_start, segment_end))
                in_segment = False

    if in_segment:
        segments.append((segment_start, len(energy) - 1))

    return segments

def determineThreshold(energy):
    mean_energy = np.mean(energy)
    std_energy = np.std(energy)
    threshold = mean_energy + 2 * std_energy
    print (threshold)

    return threshold

def drawGraphWithSegments(title, duration, yAxis, xlabel, ylabel, segments=None):
    xAxis = np.linspace(0, duration, num=len(yAxis))

    plt.plot(xAxis, yAxis)
    plt.title("Segementai laiko diagramoje")
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    if segments:
        for start, end in segments:
            plt.axvspan(xAxis[start], xAxis[end], alpha=0.3, color='green')

    plt.grid()
    plt.show()

def printInfo(channels, duration, sampWidth, fileName, minAmplitude, maxAmplitude, frameRate):
    if channels == 1:
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
frameLegthMS=30
channels, sampWidth, frameRate, numFrames, duration, fileName, frames = readFile(file)
frameLength = int(frameRate / 1000 * frameLegthMS)
maxAmplitude, minAmplitude = calculateAmplitude(sampWidth)
samples = np.frombuffer(frames, np.int16)
hopLength = int(frameLength / 2)
normalizedSamples = samples / samples.max() 

energy = calculateEnergy(normalizedSamples, frameLength, hopLength)
ZRC = calculateZRC(normalizedSamples, frameLength)

drawGraph(fileName, "laiko diagrama", duration, samples, "Laikas (s)", "Amplitudė")
drawGraph(fileName, "energijos diagrama", duration, energy, "Laikas (s)", "Energija")
drawGraph(fileName, "NKS diagrama", duration, ZRC, "Laikas (s)", "NKS")

threshold = determineThreshold(energy)
signalSegments = detectSegments(energy, threshold)
scaleFactor = len(samples) / len(energy)
scaledSignalSegments = [(int(start * scaleFactor), int(end * scaleFactor)) for start, end in signalSegments]

drawGraphWithSegments(fileName, duration, samples, "Laikas (s)", "Energija", scaledSignalSegments)
printInfo(channels, duration, sampWidth, fileName, minAmplitude, maxAmplitude, frameRate)
