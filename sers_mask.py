import nazca as nd


class SlotWaveguide:
    
    # Name of the cross-sections. Shared by all 'SlotWaveguide' objects
    _xs_wg = 'wg'
    _xs_t = 'taper'
    _xs_to = 'taper_out'
    _xs_tg = 't_gap'
    _xs_alox = 'alox'
    _xs_au = 'au'
    # Initialize the cross-sections
    nd.add_xsection(name=_xs_wg)
    nd.add_xsection(name=_xs_t)
    nd.add_xsection(name=_xs_tg)
    nd.add_xsection(name=_xs_alox)
    nd.add_xsection(name=_xs_au)
    # Keyword to put the next element on top of the previous
    putback = 'putback'

    def __init__(self, width: float, gap: float, length: float, buffer: float, label=False, label_height=3.0,
                 accuracy=0.001, point=(0, 0), entrance=0.0, taper=False, taper_length=None, taper_access=None,
                 taper_width=None,
                 taper_buffer=None, taper_out=False, taper_out_width=None, taper_out_length=None, taper_out_buffer=0.0,
                 bend=False, bend_angle=None, bend_exit=None, bend_sep=None, alumina=False,
                 alumina_length=100.0, gold=False, gold_length=50.0, metal_width=None, out_length=0.0) -> None:

        # Position attributes
        self.start = point
        self.end = point

        # General attributes
        self.asdict = {
            'width': width,
            'gap': gap,
            'length': length,
            'slot': 2 * width + gap,
            'buffer': buffer + width + gap / 2,
            # The logic for 'input' supports the depreciated 'taper_access' parameter
            'input': entrance if not taper_access or entrance != 0 else taper_access,
            # The logic for 'output' supports the depreciated 'bend_exit' parameter
            'output': bend_exit if out_length == 0 and bend_exit else out_length,
            'start': self.start,
            'end': self.end,
            'label': label,  # Not implemented
            'label_height': label_height  # Not implemented
        }

        # Taper attributes
        self.taper = {'length': taper_length if taper else 0, 'width': taper_width if taper else 0,
                      'buffer': taper_buffer if taper else 0}
        self.taperout = {'length': taper_out_length if taper_out else 0, 'width': taper_out_width if taper_out else 0,
                         'buffer': taper_out_buffer if taper_out else 0}

        # Euler bend attributes
        self.bend = {'angle': bend_angle if bend else 0, 'sep': bend_sep if bend else 0}

        # Metal mask attributes. The 'min' conditions ensures that the metal masks are within the active region
        alumina_length = min(alumina_length, length) if alumina else 0
        gold_length = min(gold_length, length) if gold else 0
        self.metals = {'alumina': alumina_length,
                       'gold': gold_length,
                       'length': alumina_length + gold_length,
                       'width': metal_width if metal_width else self.asdict['buffer']}

        self.shapes = []  # Store shapes to be inserted with the 'put' method.
        self._xs_active = self._xs_wg if not self.taper['length'] else self._xs_t  # Currently active cross-section

        # Make the waveguide and taper layers. Boolean 'XOR' operations (in for instance KLayout) must be used on
        # the layers to make the slot. Using XOR on layers means that sections with an odd number of overlapping
        # layers will be preserved, while an even number will be removed.
        self._initialize_layers(accuracy=accuracy)

        # Add the entrance
        self._add_straight(length=self.asdict['input'], width=self.taper['width'] if self.taper['width'] else 0)

        # Add a taper at the input
        if self.taper['length']:
            self._taper(self.taper['length'], self.taper['width'], self.asdict['slot'],
                        gapw1=0, gapw2=self.asdict['gap'],
                        xs=self._xs_t, xsg=self._xs_tg)

        # Active region
        self._active(self.asdict['length'],
                     metal_len=self.metals['length'], alox_len=self.metals['alumina'], au_len=self.metals['gold'],
                     xs_wg=self._xs_wg, xs_alox=self._xs_alox, xs_au=self._xs_au)

        # Add the taper after the active region
        if self.taperout['length']:
            self._taper(self.taperout['length'], self.asdict['slot'], self.taperout['width'], gapw1=self.asdict['gap'], gapw2=0,
                        xs=self._xs_to, xsg=self._xs_tg)

        # Add the Euler bend to shift the output from the input. The cross-section used is the one currently active
        if self.bend['angle']:
            self._euler(angle=self.bend['angle'], ysep=self.bend['sep'],
                        width=self.taperout['width'] if self.taperout['width'] else 0)

        # Add the output section
        self._add_straight(length=self.asdict['output'],
                           width=self.taperout['width'] if self.taperout['width'] else 0)
        # self._add_straight(xs=xs_wg, length=marg)
        # Insert structure
        self._put()

    def _initialize_layers(self, accuracy=0.001) -> None:
        """ Initializes all layers, with the given accuracy (in um). The active region contains the slot, and possibly
            metal masks. The taper cross-sections are initialized as well """

        for i, xs in enumerate((self._xs_wg, self._xs_alox, self._xs_au)):
            # Add the three waveguide layers
            nd.add_layer2xsection(xsection=xs, layer=(1, 0), accuracy=accuracy, growx=self.asdict['gap'] / 2)
            nd.add_layer2xsection(xsection=xs, layer=(1, 1), accuracy=accuracy, growx=self.asdict['slot'] / 2)
            nd.add_layer2xsection(xsection=xs, layer=(1, 2), accuracy=accuracy, growx=self.asdict['buffer'])
            # Add the alumina layer
            if i != 0 and self.metals['alumina']:
                nd.add_layer2xsection(xsection=xs, layer=(2, 0), accuracy=accuracy, growx=self.metals['width'])
            # Add the gold layer
            if i == 2 and self.metals['gold']:
                nd.add_layer2xsection(xsection=xs, layer=(3, 0), accuracy=accuracy, growx=self.metals['width'])
        # Add the main taper layer (for both input and output) and the gap layer
        if self.taper['length'] or self.taperout['length']:
            nd.add_layer2xsection(xsection=self._xs_t, layer=(1, 0), accuracy=accuracy)
            nd.add_layer2xsection(xsection=self._xs_to, layer=(1, 0), accuracy=accuracy)
            nd.add_layer2xsection(xsection=self._xs_tg, layer=(1, 2), accuracy=accuracy)
        # Add the taper buffer layers
        if self.taper['length']:
            nd.add_layer2xsection(xsection=self._xs_t, layer=(1, 1), accuracy=accuracy, growx=self.taper['buffer'])
        if self.taperout['length']:
            nd.add_layer2xsection(xsection=self._xs_to, layer=(1, 1), accuracy=accuracy, growx=self.taperout['buffer'])

    def _add_straight(self, length=0.0, width=0.0, xs=None, layer=None, edge1=None, edge2=None, edgepoints=50,
                      name=None) -> None:
        """ Simple function to append straight shapes to 'self.shapes'. It is practically the 'nd.strt()' function
            but notice that the default width and length are 0. In addition, the default cross-section is '_xs_wg' """

        xs = self._xs_active if not xs else xs
        self._xs_active = xs
        self.shapes.append(nd.strt(length=length, width=width, xs=xs, layer=layer, edge1=edge1, edge2=edge2,
                                   edgepoints=edgepoints, name=name))

    def _add_taper(self, length: [int, float], startwidth: [int, float], endwidth: [int, float],
                   xs=None) -> None:
        """ Identical to '_add_straight()', but this function adds a taper """

        xs = self._xs_active if not xs else xs
        self._xs_active = xs
        self.shapes.append(nd.taper(length=length, width1=startwidth, width2=endwidth, xs=xs))

    def _add_euler_bend(self, xs=None, width=0, angle=45) -> None:
        """ Identical to '_add_straight()', but this function adds an Euler bend """

        xs = self._xs_active if not xs else xs
        self._xs_active = xs
        self.shapes.append(nd.euler(angle=angle, xs=xs, width1=width, width2=width, radius=50))

    def _active(self, length: [int, float], metal_len=0.0, alox_len=0.0, au_len=0.0, xs_wg=None, xs_alox=None, xs_au=None):
        """ Adds the active region, including the metals masks if they exist"""

        marg = (length - metal_len) / 2
        alox_marg = (alox_len - au_len) / 2

        # Add the active region
        self._add_straight(xs=xs_wg, length=marg)
        if metal_len:
            self._metals(au_len, alox_marg, xs_alox=xs_alox, xs_au=xs_au)
        self._add_straight(xs=xs_wg, length=marg)

    def _taper(self, length: [int, float], width1: [int, float], width2: [int, float],
               gapw1=None, gapw2=None, xs=None, xsg=None) -> None:
        """ Adds a taper region with the specified start and end widths. Supports adding a taper gap if defining
            the widths 'gapw1' and 'gapw2'. The main taper will be put in the cross-section 'xs' and the gap
             in 'xgs'. """

        if gapw1 or gapw2:
            # Keyword to put the gap taper on top of the main taper
            self.shapes.append(self.putback)
            self._add_taper(length, gapw1, gapw2, xs=xsg)
        # Make main taper
        self._add_taper(length, width1, width2, xs=xs)

    def _euler(self, xs=None, width=0, angle=45, ysep=0.0) -> None:
        """ Adds an Euler bend to shift the direction of the guided wave """

        xs = self._xs_active if not xs else xs
        self._xs_active = xs
        # First Euler bend
        self._add_euler_bend(xs=xs, width=width, angle=angle)
        # Increased vertical separation of input and exit if needed
        self._add_straight(length=ysep, width=width)
        # Second Euler bend
        self._add_euler_bend(width=width, angle=-angle)

    def _metals(self, gold_length: [int, float], margin: [int, float], xs_alox=None, xs_au=None) -> None:
        """ Add the metal masks """

        if self.metals['alumina']:
            self._add_straight(length=margin, xs=xs_alox)
        if self.metals['gold']:
            self._add_straight(length=gold_length, xs=xs_au)
        if self.metals['alumina']:
            self._add_straight(length=margin, xs=xs_alox)

    def _put(self) -> None:
        """ Insert all shapes to the design. Handles gap tapers put on top of main tapers using 'put_back' """

        put_back = False
        backpoint = nd.cp.xy()

        for i, shape in enumerate(self.shapes):
            if i == 0:
                shape.put(self.asdict['start'])
            elif put_back:
                shape.put(backpoint)
                put_back = False
            elif shape != self.putback:
                # Store this point if the next shape should be put on top. Note that this is bad Nazca practice
                if i > 0 and self.shapes[i - 1] == self.putback:
                    backpoint = nd.cp.xy()
                    put_back = True
                shape.put()
        # Store endpoint
        self.end = nd.cp.xy()
        self.asdict['end'] = nd.cp.xy()
