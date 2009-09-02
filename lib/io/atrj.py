# MolMod is a collection of molecular modelling tools for python.
# Copyright (C) 2007 - 2008 Toon Verstraelen <Toon.Verstraelen@UGent.be>
#
# This file is part of MolMod.
#
# MolMod is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# MolMod is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>
#
# --
"""Reader for ATRJ files, i.e. Cerius2 Trajectory files."""


import numpy

from molmod.units import picosecond, angstrom, kcalmol
from molmod.io.common import slice_match


__all__ = ["ATRJReader", "ATRJFrame"]


class SectionFile(object):
    """A component for the ATRJReader that reads files divide into sections

       This is an internal class and should not be used directly.
    """
    def __init__(self, filename):
        self.filename = filename
        self._f = file(filename, 'r')
        self._last = self._f.readline()

    def __del__(self):
        self._f.close()

    def _get_current_label(self):
        """Get the label from the last line read"""
        if len(self._last) == 0:
            raise StopIteration
        return self._last[:self._last.find(":")]

    def _skip_section(self):
        """Skip a section"""
        self._last = self._f.readline()
        while len(self._last) > 0 and len(self._last[0].strip()) == 0:
            self._last = self._f.readline()

    def _read_section(self):
        """Read and return an entire section"""
        lines = [self._last[self._last.find(":")+1:]]
        self._last = self._f.readline()
        while len(self._last) > 0 and len(self._last[0].strip()) == 0:
            lines.append(self._last)
            self._last = self._f.readline()
        return lines

    def get_next(self, label):
        """Get the next section with the given label"""
        while self._get_current_label() != label:
            self._skip_section()
        return self._read_section()


class ATRJFrame(object):
    """A single time frame from an ATRJ file"""
    pass


class ATRJReader(object):
    """A Reader class for the ATRJ trajectory file format

       Once initialized, this object behaves like an iterator that runs over
       the individual time frames. Example usage:

       >>> foo = ATRJReader("somefile.atrj")
       >>> print foo.num_atoms
       >>> for frame in foo:
       ...    print frame.time
    """
    def __init__(self, filename, sub=slice(None)):
        """Create and ATRJReader

           Arguments:
             filename  --  the filename of the ATRJ file
             sub  --  an optional slice object to select a subset of time frames

           The number of atoms is read immediately and is available as
           self.num_atoms.
        """
        self.filename = filename
        self._sub = sub
        self._counter = 0
        self._secfile = SectionFile(filename)
        self._read_header()

    def _read_header(self):
        """Read the number of atoms from the first section"""
        self.num_atoms = int(self._secfile.get_next("FilNum")[0].split()[4])

    def __iter__(self):
        return self

    def next(self):
        """Read the next frame

           This method is part of the iterator protocol.
        """
        while True:
            # skip to the next frame
            self._secfile.get_next("Frame Number")
            if slice_match(self._sub, self._counter):
                self._counter += 1
                frame = ATRJFrame()
                # Read the time and energy
                energy_lines = self._secfile.get_next("Time/Energy")
                energy_words = energy_lines[0].split()
                frame.time = float(energy_words[0])*picosecond
                frame.step = int(energy_words[1])
                frame.total_energy = float(energy_words[2])*kcalmol
                # Read the coordinates
                coord_lines = self._secfile.get_next("Coordinates")
                frame.coordinates = numpy.zeros((self.num_atoms, 3), float)
                for index, line in enumerate(coord_lines):
                    words = line.split()
                    frame.coordinates[index, 0] = float(words[1])
                    frame.coordinates[index, 1] = float(words[2])
                    frame.coordinates[index, 2] = float(words[3])
                frame.coordinates *= angstrom
                # Done
                return frame
            else:
                self._counter += 1

