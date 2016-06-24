#!/bin/python
#
import os
import argparse

# hardcoded program numbers
# waves 11 (12 split)
# stroke 3 (4 split)
# climb 5 (8 split)
# combo 13 (33 split)
# intense 14 (2 split)
# rhythm 15 (then 16 then 17)
# audio 23
# audio3 34
# random2 32
# toggle 18 (then 19)
# orgasm 24
# torment 28
# phase 20/21/35
# phase3 22

def calltable30(mem):
#   print "Calltable 30:"
#   for k,v in mem.items():
#      print ("    %04x %02x"%(k,v))

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
      # e24 stuff didn't add yet
      r28 = mem[r26r27]
      print "*** memory[%02x%02x]=%02x"%(r31,r30,r28)
      return
   # d10
   r28&=0xe0;
   if (r28 == 0x40):
      # 0x4x_0x5x
      r28 = mem[r26r27]
      r28&= 0x1c
      r18 = r28
      r28 = mem[r26r27]
      r26r27+=1
      r28 &=3
      r2 = r28
      r26r27 = r2*256+mem[r26r27]
      # d66 stuff didn't add yet
      # d76
      r28 = r18
      if (r28 == 0):
         # dc4
         r30r31=0x8c
         if (t==1):
            r30r31+=256
         print "*** memory[%04x] = memory[%04x]"%(r30r31,r26r27)
         return
      if (r28 == 4):
         # dd2
         r30r31=0x8c
         if (t==1):
            r30r31+=256
         print "*** memory[%04x]=memory[%04x]"%(r26r27,r30r31)
         return
      if (r28 == 8):
         # 0x48-0x4a
         print "*** memory[%04x]/=2"%(r26r27)
         return
      if (r28 == 0xc):
         # 0x4b-0x4f
         print "*** memory[%04x]=rand(memory[008d],memory[008e])"%(r26r27)
         return

      oldr26r27 = r26r27
      r26r27+=1
      r2 = mem[0x21a]
      if (r28 == 0x10):
         r18 += r2
         r26r27-=1
         print "*** memory[%04x]=memory[%04x]+%02x"%(r26r27,oldr26r27,r18)
         return
      
   print "*** not implemented yet %02x"%(r28)
   
      
def calltable22(program_number):
   print "Calltable 22 with program number %d:"%(program_number)

   program_lookup = input_file[0x1c3e+ program_number]
   program_blockstart = program_lookup * 2 + 0x2000

   # code be0
   mem = {}
   mem[0x85] = 1 # temp
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

