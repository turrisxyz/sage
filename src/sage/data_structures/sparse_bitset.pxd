"""
Sparse bitset.

This is a regular bitset to which we we will add additional structure.

In particular some representation of which limbs even contain data.
"""
# ****************************************************************************
#       Copyright (C) 2020 Jonathan Kliem <jonathan.kliem@fu-berlin.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#                  https://www.gnu.org/licenses/
# ****************************************************************************

from sage.libs.gmp.types cimport *

cdef struct sparse_bitset_s:
    # The size of a bitset B counts the maximum number of bits that B can
    # hold. This size is independent of how many elements of B are toggled to
    # 1. For example, say B is the bitset 1001. Then B has size 4, with the
    # first and fourth elements toggled to 1, reading from left to right.
    # We can also think of the size of a bitset as its capacity.
    mp_bitcnt_t size

    # A limb is that part of a bitset that can fit into an mp_limb_t
    # (typically, 32 bits on a 32-bit machine and 64 bits on a 64-bit
    # machine). This counts the number of limbs to represent a bitset.
    # If a bitset has size <= n, then the whole bitset fits into a limb
    # and we only require one limb to represent the bitset. However, if
    # the bitset has size > n, we require more than one limb to
    # represent the bitset. For example, if a limb is 64 bits in length
    # and the bitset has size 96 bits, then we require at most two limbs
    # to represent the bitset.
    #
    # NOTE: some code assumes that mp_limb_t is an unsigned long
    # (this assumption is always true in practice).
    mp_size_t limbs

    # The individual bits of a bitset.
    mp_limb_t* bits

ctypedef sparse_bitset_s sparse_bitset_t[1]
