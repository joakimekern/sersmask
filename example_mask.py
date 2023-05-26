import nazca as nd
from sers_mask import SlotWaveguide

# Specify the file to which the design is written
export_path = ''
export_name = 'example.gds'
export = export_path + export_name

# Active region properties
wg_width = 0.5
wg_gap = 0.5
wg_length = 100
buffer = 3

# Multiple waveguides
number_of_waveguides = 8
waveguide_separation = 50

# Set optional properties
prop = {
    'entrance': 50,
    'out_length': 100,
    'point': (0, 0),
    'label': False,
    'label_height': 4
}
# Which components should be included?
components = {
    'taper': True,
    'taper_out': True,
    'bend': True,
    'alumina': False,
    'gold': False
}
# Taper properties
taper = {
    'taper_length': 100,
    'taper_width': 20,
    'taper_buffer': 5,
    'taper_out_length': 50,
    'taper_out_width': 10,
    'taper_out_buffer': 10
}
# Euler bend properties
euler_bend = {
    'bend_angle': 30,
    'bend_sep': 10
}
# Metal properties
metal = {
    'alumina_length': 100,
    'gold_length': 50
}

# Pack the waveguide properties
args = [wg_width, wg_gap, wg_length, buffer]
kwargs = prop | components | taper | euler_bend | metal

# Make the waveguides
waveguides = {i: [args.copy(), kwargs.copy()] for i in range(number_of_waveguides)}

# Modify the waveguides
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
    for i, (a, k) in waveguides.items():
        wg = SlotWaveguide(*a, **k)
        # Place the next waveguide above the previous
        if i < number_of_waveguides - 1:
            waveguides[i + 1][1]['point'] = (wg.start[0], wg.end[1] + waveguide_separation)
    nd.export_gds(filename=export)
