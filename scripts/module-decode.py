#!/bin/python
#
import os
import argparse

# Each Program on the ET312, either internal or User uploaded is comprised of one or more Modules
#
# When a Program is selected the ET box first sets up the 0x80+ and 0x180+ memory locations
# with stored defaults
#
# Next if you chose an internal factory Program (like say "Waves") then the firmware has a
# hardcoded mapping to what Module will be loaded first for that Program
#
# So the Module gets loaded.  This runs a set of Module instructions which is a mini language
# designed to set up the memory locations 0x80+ and 0x180+ with whatever values are required.
#
# For simple Programs they may only contain a single Module.  Once those module instructions
# have been loaded the box just gets on with running.
#
# So here's an example.  Waves loads module 11.  Module 11 contains these instructions:
# $ python3 module-decode.py -i ../firmware/312-16-decrypted.bin -d ../../buttshock-protocol-docs/doc/et312-protocol.org -m 11
# Module 11 is at 0x2014 (flash)
# memory[0086 *Multi Adjust Range Min* (0x0f)]=01
# memory[0087 *Multi Adjust Range Max* (0xff)]=40
# memory[00be *Channel A: Current Width Modulation Select* (0x04)]=41
# memory[00bb *Channel A: Current Width Modulation Increment* (0x01)]=02
# memory[00b5 *Channel A: Current Frequency Modulation Select* (0x08)]=41
# memory[00b0 *Channel A: Current Frequency Modulation Max* (0x64)]=80
#
# Some Modules will trigger other modules to run.  For example based on a timer, or based on when one of the
# current widths or frequencies reaches the end of the scale.
#
# Some Programs will also load a second Module after the first where they are programs that allow A/B to be
# split.  So in this example if not split, Waves will also load program 12:
#
# Module 12 is at 0x2026 (flash)
# memory[01bb *Channel B: Current Width Modulation Increment* (0x01)]=03
# memory[01b0 *Channel B: Current Frequency Modulation Max* (0x64)]=40
#
# This program is designed to look at the bytecode of the Module and show what it is doing
#
# These internal module numbers are hardcoded. If not split, both A and B are called
#
# waves   11 (A) 12 (B)
# stroke   3 (A)  4 (B)
# climb    5 (A)  8 (B)
# combo   13 (A) 33 (B)
# intense 14 (A)  2 (B)
# rhythm  15 (then 16 then 17)
# audio   23
# audio3  34
# random2 32 (then 32 again..)
# toggle  18 (then 19)
# orgasm  24 (then 25, 26, 27)
# torment 28
# phase   20/21/35
# phase3  22

def addresstostring(loc):
   s = "%04x"%(loc)
   if loc in memory_definitions:
      s += " "+memory_definitions[loc]
   return s

def calltable30(mem):
   # cf6
   t=0
   r30 = mem[0x85]
   if (r30 == 0):
      return
   if (not(r30 & 1)):
      t=1
   # d06
   r26r27 = 0x218
   r28 = mem[r26r27]
   if (r28 & 0x80):
      # calltable_30_set_byte
      r31 = 0
      r30 = mem[r26r27]
      r26r27+=1
      if (r30 & 0x40):
         r31 = 1
      r30 &= 0x3f;
      r30 += 0x80
      if (t==1 and r30 > 0x8c):
         r31 = 1
      r28 = mem[r26r27]
      print ("memory[%s]=%02x"%(addresstostring(r31*256+r30),r28))
      mem[r31*256+r30]=r28
      return
   # d10
   r28&=0xe0;
   if (r28 == 0x20):
      #print ("*** not implemented yet (copy a set of bytes) %02x"%(r28))
      r28 = mem[r26r27]
      r26r27+=1
      r18 = r28
      r28 &= 3
      r2 = r28
      r30 = mem[r26r27]
      r26r27+=1
      r31 = r2
      # maybe set r31 to a 1 if T set and in a certain range
      r28 = r18
      r28 &= 0x1c
      r28 = r28/4
      # e0e
      while(r28>0):
         r18 = mem[r26r27]
         r26r27+=1
         print("memory[%s]=%02x"%(addresstostring(r31*256+r30),r18))
         r30+=1
         r28-=1
      return
   if (r28 == 0x40):
      # 0x4x_0x5x d56
      r28 = mem[r26r27]
      r28&= 0x1c
      r18 = r28
      r28 = mem[r26r27]
      r26r27+=1
      r28 &=3
      r2 = r28
      r26r27 = r2*256+mem[r26r27]
      if (t==1 and mem[r26r27] > 0x8c):
         r26r27 &= 0x100;
      # d66 stuff didn't add yet
      # d76
      r28 = r18
      if (r28 == 0):
         # dc4
         r30r31=0x8c
         if (t==1):
            r30r31+=256
         print ("memory[%s]=memory[%s]"%(addresstostring(r30r31),addresstostring(r26r27)))
         return
      if (r28 == 4):
         # dd2
         r30r31=0x8c
         if (t==1):
            r30r31+=256
         print ("memory[%s]=memory[%s]"%(addresstostring(r26r27),addresstostring(r30r31)))
         return
      if (r28 == 8):
         # 0x48-0x4a
         print ("memory[%s]/=2"%(addresstostring(r26r27)))
         return
      if (r28 == 0xc):
         # 0x4b-0x4f
         print ("memory[%s]=rand(memory[%s],memory[%s])"%(addresstostring(r26r27),addresstostring(0x8d),addresstostring(0x8e)))
         return

      # d90
      r2 = mem[0x21a]
      if (r28 == 0x10):
         print ("memory[%s]+=%02x"%(addresstostring(r26r27),r2))
      if (r28 == 0x14):
         print ("memory[%s]&%02x"%(addresstostring(r26r27),r2))
      if (r28 == 0x18):
         print ("memory[%s]|%02x"%(addresstostring(r26r27),r2))
      else:
         print ("memory[%s]^%02x"%(addresstostring(r26r27),r2))
      return

   r28 = mem[r26r27]
   if (r28 & 0x10):
      print ("*** not implemented compare with store and set r15[bit1]")
      return
   print ("*** not implemented yet %02x"%(r28))

def getbyte(module, byte):
   if (module<0x80):
      return input_file[byte]
   return et312.read(byte)
   
def calltable22(program_number):

   if (program_number < 0x80):
      program_lookup = getbyte(program_number,0x1c3e+ program_number)
      program_blockstart = program_lookup * 2 + 0x2000
      print ("Module %d is at 0x%04x (flash)"%(program_number,program_blockstart))
   else:
      if (program_number < 0xa0):
         program_lookup = et312.read(0x8000+program_number-0x60)
         print("Lookup says 0x%04x"%(program_lookup))
         program_blockstart = 0x8040+program_lookup
      else:
         program_lookup = et312.read(0x8100+program_number-0xa0)
         program_blockstart = 0x8100+program_lookup
      print ("Module %d is at 0x%04x (eeprom)"%(program_number,program_blockstart))

   # code be0
   mem = {}
   mem[0x85] = 3 # temp
   r0 = getbyte(program_number,program_blockstart)
   while (r0&0xe0):
       r26r27 = 0x218
       mem[r26r27] = r0
       r26r27+=1
       # bf0
       r28 = r0 & 0xf0
       r18 = r28 # doesn't seem to be used
       if (r28 == 0x50):
           # 0xc12
           r28 = 2
       else:
           # bfa
           if ((r28&0xe0) == 0x20):
               #c00
               r28 = r0 & 0x1c
               r28 = (r28/4)+1
               r2=r28 # doesn't seem to be used
           else:
               #c0e
               r28 = 1
       # c14 copy_r28_bytes_from_blah
       while (r28 > 0):
           program_blockstart +=1;
           r0 = getbyte(program_number,program_blockstart)
           mem[r26r27] = r0
           r26r27+=1
           r28-=1
       program_blockstart +=1;
       calltable30(mem)
       r0 = getbyte(program_number,program_blockstart)

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", dest="input_file",
                    help = "Decrypted firmware to inspect")
parser.add_argument("-p", "--port", dest="port",
                    help = "port of ET box to look at user eeprom programs")
parser.add_argument("-d", "--definitions", dest="definition_file",
                    help = "Optional memory location definition file (from buttshock-protocol-docs/doc/et312-protocol.org)")
parser.add_argument("-m", "--module", dest="program_number",
                    help = "Module number to inspect (try 18 for Toggle)")
parser.add_argument("-u", "--usermode", dest="usermode",
                    help = "User mode to inspect (1-6)")
args = parser.parse_args()

if not (args.input_file or args.port):
   print("ERROR: Input file OR port required to run.")
   parser.print_help()
   exit

if (args.input_file and not args.program_number):
   print("ERROR: Module number required to run.")
   parser.print_help()
   exit

if (args.port and not (args.usermode or args.program_number)):
   print("ERROR: User mode or module required to run.")
   parser.print_help()
   exit
   
if (args.input_file):
   with open(args.input_file, "rb") as f:
      input_file = bytearray(f.read())
   program = int(args.program_number)

if (args.port):
   import sys
   sys.path.append("../../buttshock-py/")
   import buttshock.et312
   et312 = buttshock.et312.ET312SerialSync(args.port)
#   try:
#      et312.perform_handshake()
#   except buttshock.ButtshockError as e:
#      print("Handshake failed")
#      exit
   if (args.usermode):
      program = et312.read(0x8017+int(args.usermode))
      print ("user mode %d is module %d"%(int(args.usermode),program))
   else:
      program = int(args.program_number)
            
memory_definitions = {}
    
if args.definition_file:
   import re
   f = open(args.definition_file,"r")
   for line in f:
      definition = re.search('\|[^\$]+\$([0-9a-fA-F]+)[^\|]*\|\s+([^|]*)',line)
      if definition:
         memloc = int(definition.group(1),16)
         if (memloc >= 0x4000 and memloc <= 0x4fff):
            # print "%04x=%s"%(memloc-0x4000,definition.group(2))
            memory_definitions[memloc-0x4000]=definition.group(2).strip()
    
calltable22(program)

if (args.port):
   et312.write(0x4213, [0])
   et312.close()
           
   
