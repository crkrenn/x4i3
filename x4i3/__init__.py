# Modifications to this file have this license
# Copyright (c) 2020, Anatoli Fedynitch <afedynitch@gmail.com>

# This file is part of the fork (x4i3) of the EXFOR Interface (x4i)

# Please read the LICENCE.txt included in this distribution including "Our [LLNL's]
# Notice and the GNU General Public License", which applies also to this fork.

# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License (as published by the
# Free Software Foundation) version 2, dated June 1991.

# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the IMPLIED WARRANTY OF
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# terms and conditions of the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA


# Copyright (c) 2011, Lawrence Livermore National Security, LLC. Produced at
# the Lawrence Livermore National Laboratory. Written by David A. Brown
# <brown170@llnl.gov>.
#
# LLNL-CODE-484151 All rights reserved.
#
# This file is part of EXFOR Interface (x4i)
#
# Please also read the LICENSE.txt file included in this distribution, under
# "Our Notice and GNU General Public License".
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License (as published by the
# Free Software Foundation) version 2, dated June 1991.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the IMPLIED WARRANTY OF
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# terms and conditions of the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

# General info
import os
import sys

MAJOR_VERSION = 1
MINOR_VERSION = 0
PATCH = 0

__package_name__ = "x4i -- The Exfor Interface"
__version__ = '.'.join(map(str, [MAJOR_VERSION, MINOR_VERSION, PATCH]))
__author__ = 'David Brown <brown170@llnl.gov>'
__url__ = 'http://nuclear.llnl.gov/'
__license__ = 'not assigned yet'
__disclaimer__ = \
    """LLNL Disclaimer:
  This work was prepared as an account of work sponsored by an agency of the
  United States Government. Neither the United States Government nor the
  University of California nor any of their employees, makes any warranty,
  express or implied, or assumes any liability or responsibility for the
  accuracy, completeness, or usefulness of any information, apparatus, product,
  or process disclosed, or represents that its use would not infringe
  privately-owned rights.  Reference herein to any specific commercial products,
  process, or service by trade name, trademark, manufacturer or otherwise does
  not necessarily constitute or imply its endorsement, recommendation, or
  favoring by the United States Government or the University of California. The
  views and opinions of authors expressed herein do not necessarily state or
  reflect those of the United States Government or the University of California,
  and shall not be used for advertising or product endorsement purposes."""

# Common filenames
indexFileName = 'index.tbl'
dictionaryFileName = 'dictionaries.tbl'
compressedDictName = 'x4_file_db.pickle.gz'
doiFileName = 'doi.tbl'
errorFileName = 'error-entries.pickle'
coupledFileName = 'coupled-entries.pickle'
monitoredFileName = 'monitored-entries.pickle'
reactionCountFileName = 'reaction-count.pickle'
dbZipFileName = 'exfor-current.zip'
dbPath = 'db'

# Paths for standard usage
DATAPATH = os.path.abspath(os.path.join(__path__[0], '..', 'data'))
fullCompressedDictName = DATAPATH + os.sep + compressedDictName
fullIndexFileName = DATAPATH + os.sep + indexFileName
fullDictionaryFileName = DATAPATH + os.sep + dictionaryFileName
fullDoiFileName = DATAPATH + os.sep + doiFileName
fullErrorFileName = DATAPATH + os.sep + errorFileName
fullCoupledFileName = DATAPATH + os.sep + coupledFileName
fullMonitoredFileName = DATAPATH + os.sep + monitoredFileName
fullReactionCountFileName = DATAPATH + os.sep + reactionCountFileName
fullDBZipFileName = DATAPATH + os.sep + dbZipFileName
fullDBPath = DATAPATH + os.sep + dbPath

# Paths for unit testing only
TESTDATAPATH = os.sep.join(__path__ + ['test', 'data'])  # Mock db for testing
testDBPath = TESTDATAPATH + os.sep + dbPath
testIndexFileName = TESTDATAPATH + os.sep + indexFileName

from x4i3 import exfor_manager, exfor_entry

def _download_and_unpack_file(url, outfile):
    """Downloads the database files created with setup-exfor-db.py as
    a tarball and unpacks them to the correct folder."""

    from tqdm import tqdm
    import requests
    import math
    import gzip

    # Streaming, so we can iterate over the response.
    r = requests.get(url, stream=True)

    # Total size in bytes.
    total_size = int(r.headers.get('content-length', 0))
    block_size = 1024 * 1024
    wrote = 0
    with open(outfile, 'wb') as f:
        for data in tqdm(r.iter_content(block_size), total=math.ceil(total_size // block_size),
                         unit='MB', unit_scale=True):
            wrote = wrote + len(data)
            f.write(data)
    if total_size != 0 and wrote != total_size:
        raise Exception("ERROR, something went wrong")

    # Add automatic untar gunzip
    # if files not found
    # Check if files are present
    # Add tqdm to requirements


__databaseManager = exfor_manager.X4DBManagerDefault()

# In case many entries are queried subsequently, use an in-memory
# dictionary that contains all .x4 files from the db folder "-c" flag
# in get-entry.py


class DataBaseCache(dict):
    """Reads all .x4 files from db folder and strres them
    in an in-memory dictionary for faster access"""

    def __init__(self):
        self.__initialized = False

    def __load_cache(self):
        for sd in os.listdir(fullDBPath):
            for x4f in os.listdir(os.path.join(fullDBPath, sd)):
                k = sd + '/' + x4f
                dict.__setitem__(self, k, open(os.path.join(
                    fullDBPath, sd, x4f), 'rb').readlines())
        self.__initialized = True

    def __getitem__(self, key):
        if not self.__initialized:
            self.__load_cache()
        return dict.__getitem__(self, key)


database_dict = DataBaseCache()


def query(**kw): return __databaseManager.query(**kw)


def raw_retrieve(**kw): return __databaseManager.retrieve(**kw)


def retrieve(**kw):
    rr = {}
    r = __databaseManager.retrieve(**kw)
    for k, v in r.items():
        rr[k] = exfor_entry.X4Entry(v)
    return rr


__all__ = [
    '__init__', 'exfor_dataset', 'exfor_exceptions', 'exfor_manager', 'exfor_reference', 'exfor_utilities',
    'endl_Z', 'exfor_dicts', 'exfor_field', 'exfor_particle', 'exfor_section', 'pyparsing',
    'exfor_column_parsing', 'exfor_entry', 'exfor_grammers', 'exfor_reactions', 'exfor_subentry'
]
