# sersmask
Python library to create a lithography mask for SERS waveguides in gds format.

IMPORTANT: This library uses Nazca to create waveguides. Nazca is not in the pip libraries, and must be donwloaded and installed manually. See https://nazca-design.org/installation/ for instructions.

A single class is defined in 'sersmask.py', the 'SlotWaveguide'. Its arguments are all the relevant parameters needed to create a slot waveguide intended for SERS sensing. An example of how to use the class is found in 'example_mask.py'. The resulting mask is found in 'example_mask.gds'.

Note however, that every design must be subject to XOR logical operation on layers (1, 0), (1, 1), and (1, 2) to produce the final mask. Nazca does not provide the possibility of boolean operations, so these operations must be done manually. One way to do this is with KLayout, which is a free mask file editing software. Opening the final mask with Klayout, go to Edit --> Layers --> Boolean Operations (image A). Then select 1/0 as source A and 1/1 (or 1/2) as source B, XOR as mode and 1/0 as result (images B and C). Doing the boolean operation twice (once on 1/1 and once on 1/2) produces the final mask.

Image A:
![image](https://github.com/joakimekern/sersmask/assets/134723654/bc0f8a97-a7f7-4963-b756-7c4cbfd205c0)

Image B:
![image](https://github.com/joakimekern/sersmask/assets/134723654/38c9765b-1405-4f04-98e6-8e43938205c5)

Image C:
![image](https://github.com/joakimekern/sersmask/assets/134723654/2a84d656-5297-4cb5-bae6-de8d566492f4)

