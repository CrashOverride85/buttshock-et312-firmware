#!/bin/python
#
import os
import argparse

def calltable30(mem):
   print "Calltable 30 with:"
   for k,v in mem.items():
      print ("    %04x %02x"%(k,v))

def calltable22(program_number):
   print "Calltable 22 with program number %d:"%(program_number)

   program_lookup = input_file[0x1c3e+ program_number]
   program_blockstart = program_lookup * 2 + 0x2000

   # code be0
   mem = {}
   r0 = input_file[program_blockstart]
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
           r0 = input_file[program_blockstart]
           mem[r26r27] = r0
           r26r27+=1
           r28-=1
       program_blockstart +=1;
       calltable30(mem)
       r0 = input_file[program_blockstart]


parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", dest="input_file",
                    help = "Decrypted firmware to inspect")
parser.add_argument("-p", "--program", dest="program_number",
                    help = "Program number to inspect (try 18 for toggle part 1)")
args = parser.parse_args()

if not args.input_file:
   print("ERROR: Input file required to run.")
   parser.print_help()

if not args.program_number:
   print("ERROR: Program number required to run.")
   parser.print_help()
   
with open(args.input_file, "rb") as f:
    input_file = bytearray(f.read())

calltable22(int(args.program_number))

