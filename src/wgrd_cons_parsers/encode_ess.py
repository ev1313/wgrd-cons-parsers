#!/usr/bin/env python3
# Based on https://zenhax.com/viewtopic.php?f=6&t=3324


import wave
import sys
import argparse
import pathlib

from .utils import *

def initEncoder():
  num9 = 0
  num10 = 0
  num8 = 0
  num12 = 0
  num6 = 0
  num7 = 0
  num11 = 0
  num13 = 0
  num14 = 0
  num15 = 0
  return num9, num10, num8, num12, num6, num7, num11, num13, num14, num15

def encodeBlock(fo, array, list, num9, num10, num8, num12, num6, num7, num11, num13, num14, num15):

  num5 = len(array)

  array2 = [0] * num5
  array3 = [0] * num5
  array4 = [0] * num5

  write16sb(fo, num9)
  write16sb(fo, num10)
  write16sb(fo, num8)
  write16sb(fo, num12)
  write16sb(fo, num6)
  write16sb(fo, num7)
  write16sb(fo, num11)
  write16sb(fo, num13)
  write16sb(fo, num14)
  write16sb(fo, num15)

  for j in range(num5):
    num17 = num8
    num18 = 2 * (2 * num6 - num11) - 5 * num7
    num19 = 2 * num8 - num12
    num20 = num7
    num7 = num6
    num21 = (num10 * num18 + 128 >> 8) + (num9 * num19 + 128 >> 8)
    num22 = 0
    num23 = array[j] - num21
    if (num23 < 0):
      num22 = 1
      num23 = ~num23
    array4[j] = 0
    num24 = 0
    if (num23 > 0):
      if (num23 >= num13 + num14):
        if (num15 > 0):
          num25 = (num23 - num13 - num14) // num15
          num24 = num25 + 2
          array4[j] = (num23 - num13 - num14 - num15 * num25) * 4 // num15
        else:
          num24 = 3
      elif (num23 >= num13):
        num24 = 1
        if (num14 > 0):
          array4[j] = (num23 - num13) * 4 // num14
      elif (num13 > 0):
        array4[j] = num23 * 4 // num13
    num24 <<= 1
    num24 += num22
    array3[j] = num24
    num26 = 0
    num24 = array3[j]
    if (num24 > 1):
      if (num24 > 3):
        if (num24 > 5):
          num26 = num13 + num14 + (num15 + 1) * ((num24 >> 1) - 2)
          num27 = num15 + num26
          num13 += 6 * ((num13 + 2048) // 2048)
          num14 += 6 * ((num14 + 1024) // 1024)
          num15 += 6 * ((num15 + 512) // 512)
        else:
          num26 = num14 + num13
          num27 = num15 + num26
          num13 += 6 * ((num13 + 2048) // 2048)
          num14 += 6 * ((num14 + 1024) // 1024)
          num15 -= 2 * ((num15 + 510) // 512)
      else:
        num26 = num13
        num27 = num14 + num13
        num13 += 6 * ((num13 + 2048) // 2048)
        num14 -= 2 * ((num14 + 1022) // 1024)
    else:
      num27 = num13
      num13 -= 2 * ((num13 + 2046) // 2048)
    num28 = num27 + num26 >> 1
    if (num28 > num13):
      if (num28 > num14):
        if (num28 <= num15):
          num15 -= 2 * ((num15 + 510) // 512)
      else:
        num14 -= 2 * ((num14 + 1022) // 1024)
    else:
      num13 -= 2 * ((num13 + 2046) // 2048)
    if (num27 - num26 > 64):
      num29 = (num27 - num26) // 4 + 1
      num28 = num26 + num29 * array4[j]
    else:
      array4[j] = -1
    if ((num24 & 1) > 0):
      num28 = ~num28
    array2[j] = num28
    num30 = array2[j]
    num6 = num30 + (num10 * num18 + 128 >> 8)

    # ???
    if ((num18 | num30) != 0):
      num10 += (((num18 ^ num30) & -536870913) | 0x40000000) >> 29
    num31 = num6 + (num9 * num19 + 128 >> 8)

    # Clamp
    if (num31 > 32767):
      num31 = 32767
    if (num31 < -32768):
      num31 = -32768

    # ???
    if ((num6 | num19) != 0):
      num9 += (((num6 ^ num19) & -536870913) | 0x40000000) >> 29

    num12 = num17
    num8 = num31
    num11 = num20

  for j in range(num5):
    num25 = array3[j]
    if (num25 > 23):
      list += [False] * 24
      list += [True]
      num24 = num25 - 24

      # Encode num24 in 16 bits
      for l in range(16):
        if ((num24 & 0x8000) == 0):
          list += [False]
        else:
          list += [True]
        num24 <<= 1
    else:
      list += [False] * num25
      list += [True]

    if (array4[j] != -1):
      if (array4[j] < 2):
        list += [False]
      else:
        list += [True]
      if ((array4[j] & 1) == 0):
        list += [False]
      else:
        list += [True]

  return list, (num9, num10, num8, num12, num6, num7, num11, num13, num14, num15)

def bitsToBytes(list):
  # Ensure we have the necessary amount of bits
  if (len(list) % 8 != 0):
    list += [False] * 8

  data = b''
  for j in range(len(list) // 8):
    num24 = 0
    for num32 in range(8):
      num24 *= 2
      if (list[j * 8 + num32]):
        num24 += 1
    data += bytes([num24])

  return data


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("path", type=pathlib.Path, help="path to the wave file")
  parser.add_argument("-o", "--output", type=pathlib.Path, default="test.ess",
                      help="path to the output ess file")
  args = parser.parse_args()

  #print("Loading '%s'" % path)

  data = open(args.path, "rb").read()
  f = BytesIO(data)

  wav = wave.open(f, 'rb')
  nchannels = wav.getnchannels()
  sampwidth = wav.getsampwidth()
  assert(sampwidth == 16 // 8)
  framerate = wav.getframerate()
  assert(framerate < 0xFFFF)
  nframes = wav.getnframes()
  comptype = wav.getcomptype()
  assert(comptype == 'NONE')
  #FIXME: wav.getcompname()

  channelCount = nchannels
  samplerate = framerate
  frameCount = nframes
  frameSize = nchannels * sampwidth

  if channelCount == 1:
    blockMaxFrameCount = 1024 // 1
  elif channelCount == 2:
    blockMaxFrameCount = 1024 // 2
  elif channelCount == 6:
    blockMaxFrameCount = 1024 // 6
  else:
    assert(False)

  fo = open(args.output, 'wb')

  # Write header
  write32b(fo, 0x01000202)
  write8(fo, 0x01) #isShort
  write8(fo, channelCount)
  write16b(fo, samplerate)
  write32b(fo, frameCount)
  write32b(fo, 0)
  write32b(fo, frameCount)

  # Calculate number of blocks
  blockCount = (frameCount + (blockMaxFrameCount - 1)) // blockMaxFrameCount
  #print("Number of blocks: %d" % blockCount)

  # Skip block offsets
  fo.seek(blockCount * 4, 1)

  dataOffset = fo.tell()

  # Initialize encoders
  channelEncoders = []
  for channelIndex in range(channelCount):
    channelEncoder = initEncoder()
    channelEncoders += [channelEncoder]

  blockOffsets = []
  for blockIndex in range(blockCount):
    #print("%d / %d" % (blockIndex, blockCount))

    frameData = wav.readframes(blockMaxFrameCount)
    assert(len(frameData) % frameSize == 0)
    blockFrameCount = len(frameData) // frameSize

    # Deinterleave audio
    channelsData = []
    for channelIndex in range(channelCount):
      channelData = []
      for frameIndex in range(blockFrameCount):
        channelData += [ctypes.c_int16.from_buffer_copy(frameData, frameIndex * frameSize + channelIndex * 2).value]
      channelsData += [channelData]

    blockDataBits = []
    for channelIndex in range(channelCount):
      blockDataBits, channelEncoders[channelIndex] = encodeBlock(fo, channelsData[channelIndex], blockDataBits, *channelEncoders[channelIndex])
    fo.write(bitsToBytes(blockDataBits))

    # Remember block size
    blockOffsets += [fo.tell() - dataOffset]

  # Write block offsets
  fo.seek(20)
  for blockIndex in range(blockCount):
    blockOffset = blockOffsets[blockIndex]
    write32b(fo, blockOffset)
