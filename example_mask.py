import nazca as nd  # NOTE: Not in the pip libraries. See installation guide at: https://nazca-design.org/installation/
from sersmask import SlotWaveguide

# Specify the file to which the design is written
export_path = ''
export_name = 'example.gds'
export = export_path + export_name

# Active region properties. All units are in microns
wg_width = 0.5      # Width of each rail in the slot
wg_gap = 0.5        # Distance between the rails
wg_length = 100     # Length of the active region
buffer = 3          # Buffer region separating the waveguide structure from the SiN thin film

# Multiple waveguides
number_of_waveguides = 8
waveguide_separation = 50   # In microns

# Set optional properties. All units are in microns
prop = {
    'entrance': 50,     # Input length
    'out_length': 100,  # Output length
    'point': (0, 0),    # The start point, i.e., the westernmost point of the waveguide
    'label': False,     # Not implemented
    'label_height': 4,  # Not implemented
# Which components should be included?
    'taper': True,      # Include input taper
    'taper_out': True,  # Include output taper
    'bend': True,       # Include Euler bend
    'alumina': False,   # Include alumina layer mask
    'gold': False,      # Include gold layer mask
# Taper properties
    'taper_length': 100,    # Length of the taper
    'taper_width': 20,      # Start width
    'taper_buffer': 5,      # Buffer region between the taper and SiN thin film
    'taper_out_length': 50, # Length of the output taper
    'taper_out_width': 10,  # End width of the output taper
    'taper_out_buffer': 10, # Output buffer
# Euler bend properties
    'bend_angle': 30,
    'bend_sep': 10,     # Additional vertical seperation between the Euler bends
# Metal properties
    'alumina_length': 100,
    'gold_length': 50,
}

# Pack the waveguide properties
args = [wg_width, wg_gap, wg_length, buffer]
kwargs = prop

# Store the waveguide properties
waveguides = {i: [args.copy(), kwargs.copy()] for i in range(number_of_waveguides)}

# Modify the waveguide properties
waveguides[1][1]['taper'] = False

waveguides[2][1]['taper_out'] = False

waveguides[3][1]['bend'] = False

waveguides[4][1]['taper'] = False
waveguides[4][1]['taper_out'] = False

waveguides[5][1]['taper_out'] = False
waveguides[5][1]['bend'] = False

waveguides[6][1]['bend'] = False
waveguides[6][1]['taper'] = False

waveguides[7][1]['taper'] = False
waveguides[7][1]['taper_out'] = False
waveguides[7][1]['bend'] = False

if __name__ == '__main__':
    # Iterate through the waveguides and place them in the design
    for i, (a, k) in waveguides.items():
        wg = SlotWaveguide(*a, **k)
        # Place the next waveguide above the previous
        if i < number_of_waveguides - 1:
            waveguides[i + 1][1]['point'] = (wg.start[0], wg.end[1] + waveguide_separation)
    nd.export_gds(filename=export)
