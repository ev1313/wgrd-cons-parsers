#!/usr/bin/env python3
# Based on https://zenhax.com/viewtopic.php?f=6&t=3324

import sys
import wave
import argparse
import pathlib

from .utils import *


def decodeBlock(f, num19, array4, num7):

  array3 = [0] * num7
  array2 = [0] * num7

  num9 = read16sb(f)
  num10 = read16sb(f)
  num11 = read16sb(f)
  num12 = read16sb(f)
  num13 = read16sb(f)
  num14 = read16sb(f)
  num15 = read16sb(f)
  num16 = read16sb(f)
  num17 = read16sb(f)
  num18 = read16sb(f)
  num20 = num19 - 1

  sampleIndex = 0
  while sampleIndex < num7:
    num21 = (array4[num19 // 8] >> 7 - num19 % 8) & 1
    if (num21 > 0):
      num22 = 0
      num23 = num19 - num20 - 1
      num20 = num19
      if (num23 >= 2):
        if (num23 >= 4):
          if (num23 >= 6):
            if (num23 == 24):
              num24 = 0
              for k in range(16):
                num19 += 1
                num24 = num24 * 2 + ((array4[num19 // 8] >> 7 - num19 % 8) & 1)
                num20 += 1
              num23 = num24 + 24

            num25 = num18
            num26 = num17
            num22 = num16 + num26 + (num25 + 1) * ((num23 >> 1) - 2)
            num8 = num25 + num22
            num16 += 6 * ((num16 + 2048) // 2048)
            num17 = num26 + 6 * ((num26 + 1024) // 1024)
            num18 = num25 + 6 * ((num25 + 512) // 512)
          else:
            num27 = num17
            num28 = num18
            num22 = num27 + num16
            num8 = num28 + num22
            num16 += 6 * ((num16 + 2048) // 2048)
            num17 = num27 + 6 * ((num27 + 1024) // 1024)
            num18 = num28 - 2 * ((num28 + 510) // 512)
        else:
          num22 = num16
          num29 = num17
          num8 = num29 + num16
          num16 = num22 + 6 * ((num22 + 2048) // 2048)
          num17 = num29 - 2 * ((num29 + 1022) // 1024)
        num30 = num8
      else:
        num30 = num16
        num16 -= 2 * ((num16 + 2046) // 2048)
      num31 = num30 + num22 >> 1

      # FIXME: Simplify?
      if (num31 > num16):
        if (num31 > num17):
          if (num31 <= num18):
            num18 -= 2 * ((num18 + 510) // 512)
        else:
          num17 -= 2 * ((num17 + 1022) // 1024)
      else:
        num16 -= 2 * ((num16 + 2046) // 2048)

      num32 = num30 - num22
      if (num32 > 64):
        num33 = num32 // 4 + 1
        num19 += 1
        num21 = (array4[num19 // 8] >> 7 - num19 % 8) & 1
        num19 += 1
        num34 = num21 * 2 + ((array4[num19 // 8] >> 7 - num19 % 8) & 1)
        num20 += 2
        num31 = num22 + num33 * num34
      if ((num23 & 1) > 0):
        num31 = ~num31
      array3[sampleIndex] = num31
      sampleIndex += 1
    num19 += 1

  for sampleIndex in range(num7):
    num35 = array3[sampleIndex]
    num27 = num11
    num36 = 2 * (2 * num13 - num15) - 5 * num14
    num37 = 2 * num11 - num12
    num38 = num14
    num14 = num13
    num13 = num35 + (num10 * num36 + 128 >> 8)

    # ???
    if ((num36 | num35) != 0):
      num10 += (((num36 ^ num35) & -536870913) | 0x40000000) >> 29

    sample = num13 + (num9 * num37 + 128 >> 8)

    # Clamp sample
    if (sample > 32767):
      sample = 32767
    if (sample < -32768):
      sample = -32768

    # ???
    if ((num13 | num37) != 0):
      num9 += (((num13 ^ num37) & -536870913) | 0x40000000) >> 29

    num12 = num27
    array2[sampleIndex] = sample
    num11 = sample
    num15 = num38

  return num19, array2

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("path", type=pathlib.Path, help="path to the ess file")
  parser.add_argument("-o", "--output", type=pathlib.Path, default="test.ess.wav",
                           help="path to the output wav file")
  args = parser.parse_args()

  #print("Loading '%s'" % path)

  data = open(args.path, "rb").read()
  f = BytesIO(data)

  unk0 = read32b(f)
  unk1 = read8(f)
  channelCount = read8(f)
  samplerate = read16b(f)
  frameCount1 = read32b(f)
  unk2 = read32b(f)
  frameCount2 = read32b(f)
  #print("ESS unk0=0x%08X unk1=0x%X channelCount=%d samplerate=%dHz frameCount1=%d unk2=0x%X frameCount2=%d" % (unk0, unk1, channelCount, samplerate, frameCount1, unk2, frameCount2))
  assert(unk0 == 0x01000202)

  # These are mostly 0, I assume it's the number of bits
  assert(unk1 in [0, 1])

  #FIXME: Many values, see sformat.py for more
  #assert(unk2 in [0x0, 0xC0])

  # These are mostly the same, but sometimes frameCount1 is higher?!
  # Number of blocks seems to match frameCount1
  # If this wasn't the case, I'd suspect that frameCount1 is the decoded length (including silence)
  assert(frameCount1 >= frameCount2)

  if channelCount == 1:
    blockMaxFrameCount = 1024 // 1
  elif channelCount == 2:
    blockMaxFrameCount = 1024 // 2
  elif channelCount == 6:
    # All files I've seen are actually 3x stereo tracks
    # The generated files work fine in Audacity, but other tools might have limited support
    blockMaxFrameCount = 1024 // 6
  else:
    assert(False)

  fo = open(args.output, "wb")
  wav = wave.open(fo, 'wb')
  wav.setsampwidth(2)
  wav.setnchannels(channelCount)
  wav.setframerate(samplerate)
  wav.setnframes(frameCount1)

  # Calculate number of blocks
  blockCount = (frameCount1 + (blockMaxFrameCount - 1)) // blockMaxFrameCount
  #print("Number of blocks: %d" % blockCount)

  # Store block offsets
  blockOffsets = [0]
  for blockIndex in range(blockCount):
    blockOffset = read32b(f)
    blockOffsets += [blockOffset]

  dataOffset = f.tell()

  for blockIndex in range(blockCount):
    #print("%d / %d" % (blockIndex, blockCount))
    blockDataSize = blockOffsets[blockIndex + 1] - blockOffsets[blockIndex] - 20 * channelCount

    blockFrameCount = min(frameCount1, blockMaxFrameCount)

    blockOffset = blockOffsets[blockIndex]
    f.seek(dataOffset + blockOffset + 20 * channelCount)
    blockData = f.read(blockDataSize)
    f.seek(dataOffset + blockOffset)

    blockDataOffset = 0
    channelsData = []
    for channelIndex in range(channelCount):
      blockDataOffset, channelData = decodeBlock(f, blockDataOffset, blockData, blockFrameCount)
      channelsData += [channelData]

    # Interleave audio
    frameData = b''
    for frameIndex in range(blockFrameCount):
      for channelIndex in range(channelCount):
        frameData += encode16s(channelsData[channelIndex][frameIndex])

    wav.writeframes(frameData)

    frameCount1 -= blockFrameCount
