r"""
Fourier expansions of classical weak Jacobi forms.

AUTHOR:

- Martin Raum
"""

#===============================================================================
# 
# Copyright (C) 2010-2014 Martin Raum
# 
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful, 
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.
#
#===============================================================================

from sage.combinat.dict_addition import dict_linear_combination
from sage.matrix.all import matrix
from sage.misc.all import isqrt, cached_function
from sage.modular.jacobi.classical_weak import classical_weak_jacobi_fe_indices, classical_weak_jacobi_forms
from sage.rings.all import Integer, ZZ

# We do not implement this separately, because this is the same
# reduction as in the case of weak Jacobi forms.
from sage.modular.jacobi.classical_weak import reduce_classical_jacobi_fe_index

def classical_jacobi_fe_indices(m, prec, reduced=False):
    r"""
    Indices `(n,r)` of Fourier expansions of Jacobi forms of index `m`.

    INPUT:

    - `m` -- A positive integer.

    - ``prec`` -- A non-negative integer.

    - ``reduce`` -- A boolean (default: ``False``).  If ``True``
                    restrict to `0 \le r \le m`.

    OUTPUT:

    A generator of pairs of integers `(n,r)`.

    EXAMPLES::

        sage: from sage.modular.jacobi.all import *
        sage: list(classical_jacobi_fe_indices(2, 3, True))
        [(1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2), (0, 0)]
        sage: list(classical_jacobi_fe_indices(2, 3, False))
        [(1, 0), (1, 1), (1, -1), (1, 2), (1, -2), (2, 0), (2, 1), (2, -1), (2, 2), (2, -2), (2, 3), (2, -3), (0, 0), (2, 4), (2, -4)]
    """
    fm = Integer(4*m)

    if reduced :
        # positive definite forms
        for n in range(1, prec):
            for r in range(min(m + 1, isqrt(fm * n - 1) + 1)):
                yield (n, r)

        # indefinite forms
        for r in xrange(0, min(m+1, isqrt((prec-1) * fm) + 1) ):
            if fm.divides(r**2) :
                yield (r**2 // fm, r)
    else :
        # positive definite forms
        for n in range(1, prec):
            yield(n, 0)
            for r in range(1, isqrt(fm * n - 1) + 1):
                yield (n, r)
                yield (n, -r)

        # indefinite forms
        if prec > 0:
            yield (0,0)
        for n in xrange(1, prec):
            if (fm * n).is_square():
                rt_fmm = isqrt(fm * n)
                yield(n, rt_fmm)
                yield(n, -rt_fmm)
        
    raise StopIteration

@cached_function
def _classical_jacobi_forms_as_weak_jacobi_forms(k, m, algorithm="skoruppa"):
    r"""
    The coordinates of Jacobi forms with respect to a basis of
    classical weak Jacobi forms computed using the given algorithm.
    
    INPUT:
    
    - `k -- An integer.
    
    - `m` -- A non-negative integer.

    - ``algorithm`` -- Default: ''skoruppa''.  Only ''skoruppa'' is implemented.

    OUTPUT:

    A list of vectors.
    
    EXAMPLES::
    
        sage: from sage.modular.jacobi.classical import _classical_jacobi_forms_as_weak_jacobi_forms
        sage: _classical_jacobi_forms_as_weak_jacobi_forms(10, 1)
        [
        (1, 0, 0),
        (0, 0, 1)
        ]
        sage: _classical_jacobi_forms_as_weak_jacobi_forms(12, 1)
        [
        (1, 0, 0),
        (0, 1, 0)
        ]
    """
    prec = m//4 + 1
    weak_forms = classical_weak_jacobi_forms(k, m, prec, algorithm)
    indices = list(classical_weak_jacobi_fe_indices(m, prec, reduced=True))
    weak_index_matrix = \
        matrix(ZZ, [ [ (f[(n,r)] if (n,r) in f else 0) for (n,r) in indices
                       if 4*m*n - r**2 < 0 ] for f in weak_forms] )
        
    return weak_index_matrix.left_kernel().echelonized_basis()

def classical_jacobi_forms(k, m, prec, algorithm="skoruppa"):
    r"""
    Compute Fourier expansions of classical Jacobi forms of weight `k`
    and index `m`.

    INPUT:
    
    - `k -- An integer.
    
    - `m` -- A non-negative integer.

    - ``prec`` -- A non-negative integer that corresponds to a
                  precision of the `q`-expansion.

    - ``algorithm`` -- Default: ''skoruppa''.  Only ''skoruppa'' is
                       implemented.

    OUTPUT:

    A list of dictionaries, mapping indices `(n,r)` to rationals.

    EXAMPLES:

        sage: from sage.modular.jacobi.classical import *
        sage: k = 4; m = 2; prec = 5
        sage: classical_jacobi_forms(k, m, prec)
        [{(1, 2): 564480, (3, 2): 33868800, (0, 0): 40320, (3, 0): 51932160, (3, 1): 54190080, (2, 1): 18063360, (1, 1): 2580480, (2, 0): 23143680, (2, 2): 11289600, (4, 2): 95477760, (1, 0): 3386880, (4, 1): 108380160, (4, 0): 138862080}]

    TESTS:

    See ``test_classical.py``.
    """
    weak_forms = classical_weak_jacobi_forms(k, m, prec, algorithm)
    coords = _classical_jacobi_forms_as_weak_jacobi_forms(k, m)

    return [dict_linear_combination(zip(weak_forms, cs)) for cs in coords]
