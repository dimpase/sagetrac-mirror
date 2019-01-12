"""
Singular's Groebner Strategy Objects

AUTHORS:

- Martin Albrecht (2009-07): initial implementation
- Michael Brickenstein (2009-07): initial implementation
- Hans Schoenemann (2009-07): initial implementation
"""

#*****************************************************************************
#       Copyright (C) 2009 Martin Albrecht <M.R.Albrecht@rhul.ac.uk>
#       Copyright (C) 2009 Michael Brickenstein <brickenstein@mfo.de>
#       Copyright (C) 2009 Hans Schoenemann <hannes@mathematik.uni-kl.de>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
#*****************************************************************************

cdef extern from *: # hack to get at cython macro
    int unlikely(int)
    int likely(int)

from sage.structure.richcmp cimport richcmp
from sage.libs.singular.decl cimport ideal, ring, poly, currRing
from sage.libs.singular.decl cimport rChangeCurrRing
from sage.libs.singular.decl cimport new_skStrategy, delete_skStrategy, id_RankFreeModule
from sage.libs.singular.decl cimport initEcartBBA, enterSBba, initBuchMoraCrit, initS, pNorm, id_Delete, kTest
from sage.libs.singular.decl cimport omfree, redNF, p_Copy, redtailBba

from sage.libs.singular.ring cimport singular_ring_reference, singular_ring_delete

from sage.rings.polynomial.multi_polynomial_ideal import MPolynomialIdeal, NCPolynomialIdeal
from sage.rings.polynomial.multi_polynomial_ideal_libsingular cimport sage_ideal_to_singular_ideal
from sage.rings.polynomial.multi_polynomial_libsingular cimport MPolynomial_libsingular, MPolynomialRing_libsingular, new_MP
from sage.rings.polynomial.plural cimport new_NCP

cdef class GroebnerStrategy(SageObject):
    """
    A Wrapper for Singular's Groebner Strategy Object.

    This object provides functions for normal form computations and
    other functions for Groebner basis computation.

    ALGORITHM:

    Uses Singular via libSINGULAR
    """
    def __cinit__(self, L):
        """
        Create a new :class:`GroebnerStrategy` object for the
        generators of the ideal ``L``.

        INPUT:

        - ``L`` - a multivariate polynomial ideal

        EXAMPLES::

            sage: from sage.libs.singular.groebner_strategy import GroebnerStrategy
            sage: P.<x,y,z> = PolynomialRing(QQ)
            sage: I = Ideal([x+z,y+z+1])
            sage: strat = GroebnerStrategy(I); strat
            Groebner Strategy for ideal generated by 2 elements
            over Multivariate Polynomial Ring in x, y, z over Rational Field

        TESTS::

            sage: from sage.libs.singular.groebner_strategy import GroebnerStrategy
            sage: strat = GroebnerStrategy(None)
            Traceback (most recent call last):
            ...
            TypeError: First parameter must be a multivariate polynomial ideal.

            sage: P.<x,y,z> = PolynomialRing(QQ,order='neglex')
            sage: I = Ideal([x+z,y+z+1])
            sage: strat = GroebnerStrategy(I)
            Traceback (most recent call last):
            ...
            NotImplementedError: The local case is not implemented yet.

            sage: P.<x,y,z> = PolynomialRing(CC,order='neglex')
            sage: I = Ideal([x+z,y+z+1])
            sage: strat = GroebnerStrategy(I)
            Traceback (most recent call last):
            ...
            TypeError: First parameter's ring must be multivariate polynomial ring via libsingular.

            sage: P.<x,y,z> = PolynomialRing(ZZ)
            sage: I = Ideal([x+z,y+z+1])
            sage: strat = GroebnerStrategy(I)
            Traceback (most recent call last):
            ...
            NotImplementedError: Only coefficient fields are implemented so far.

        """
        if not isinstance(L, MPolynomialIdeal):
            raise TypeError("First parameter must be a multivariate polynomial ideal.")

        if not isinstance(L.ring(), MPolynomialRing_libsingular):
            raise TypeError("First parameter's ring must be multivariate polynomial ring via libsingular.")

        self._ideal = L

        cdef MPolynomialRing_libsingular R = <MPolynomialRing_libsingular>L.ring()
        self._parent = R
        self._parent_ring_ref = R._ring_ref
        self._parent_ring = singular_ring_reference(R._ring, self._parent_ring_ref)

        if not R.term_order().is_global():
            raise NotImplementedError("The local case is not implemented yet.")

        if not R.base_ring().is_field():
            raise NotImplementedError("Only coefficient fields are implemented so far.")

        if (R._ring != currRing):
            rChangeCurrRing(R._ring)

        cdef ideal *i = sage_ideal_to_singular_ideal(L)
        self._strat = new_skStrategy()

        self._strat.ak = id_RankFreeModule(i, R._ring)
        #- creating temp data structures
        initBuchMoraCrit(self._strat)
        self._strat.initEcart = initEcartBBA
        self._strat.enterS = enterSBba
        #- set S
        self._strat.sl = -1
        #- init local data struct
        initS(i, NULL, self._strat)

        cdef int j
        cdef bint base_ring_is_field = R.base_ring().is_field()
        if (R._ring != currRing):
            rChangeCurrRing(R._ring)
        if base_ring_is_field:
            for j in range(self._strat.sl, -1, -1):
                pNorm(self._strat.S[j])

        id_Delete(&i, R._ring)
        kTest(self._strat)

    def __dealloc__(self):
        """
        TESTS::

            sage: from sage.libs.singular.groebner_strategy import GroebnerStrategy
            sage: P.<x,y,z> = PolynomialRing(GF(32003))
            sage: I = Ideal([x + z, y + z])
            sage: strat = GroebnerStrategy(I)
            sage: del strat
        """
        # WARNING: the Cython class self._parent is no longer accessible!
        # see http://trac.sagemath.org/sage_trac/ticket/11339
        cdef ring *oldRing = NULL
        if self._strat:
            omfree(self._strat.sevS)
            omfree(self._strat.ecartS)
            omfree(self._strat.T)
            omfree(self._strat.sevT)
            omfree(self._strat.R)
            omfree(self._strat.S_2_R)
            omfree(self._strat.L)
            omfree(self._strat.B)
            omfree(self._strat.fromQ)
            id_Delete(&self._strat.Shdl, self._parent_ring)

            if self._parent_ring != currRing:
                oldRing = currRing
                rChangeCurrRing(self._parent_ring)
                delete_skStrategy(self._strat)
                rChangeCurrRing(oldRing)
            else:
                delete_skStrategy(self._strat)
        singular_ring_delete(self._parent_ring, self._parent_ring_ref)

    def show_refs(self):
        print <long>(self._parent_ring),"with",self._parent_ring_ref[0],"references"
        print <long>(self._strat)

    def _repr_(self):
        """
        TESTS::

            sage: from sage.libs.singular.groebner_strategy import GroebnerStrategy
            sage: P.<x,y,z> = PolynomialRing(GF(32003))
            sage: I = Ideal([x + z, y + z])
            sage: strat = GroebnerStrategy(I)
            sage: strat # indirect doctest
            Groebner Strategy for ideal generated by 2 elements over
            Multivariate Polynomial Ring in x, y, z over Finite Field of size 32003
        """
        return "Groebner Strategy for ideal generated by %d elements over %s"%(self._ideal.ngens(),self._parent)

    def ideal(self):
        """
        Return the ideal this strategy object is defined for.

        EXAMPLES::

            sage: from sage.libs.singular.groebner_strategy import GroebnerStrategy
            sage: P.<x,y,z> = PolynomialRing(GF(32003))
            sage: I = Ideal([x + z, y + z])
            sage: strat = GroebnerStrategy(I)
            sage: strat.ideal()
            Ideal (x + z, y + z) of Multivariate Polynomial Ring in x, y, z over Finite Field of size 32003
        """
        return self._ideal

    def ring(self):
        """
        Return the ring this strategy object is defined over.

        EXAMPLES::

            sage: from sage.libs.singular.groebner_strategy import GroebnerStrategy
            sage: P.<x,y,z> = PolynomialRing(GF(32003))
            sage: I = Ideal([x + z, y + z])
            sage: strat = GroebnerStrategy(I)
            sage: strat.ring()
            Multivariate Polynomial Ring in x, y, z over Finite Field of size 32003
        """
        return self._parent

    def __richcmp__(self, other, op):
        """
        EXAMPLES::

            sage: from sage.libs.singular.groebner_strategy import GroebnerStrategy
            sage: P.<x,y,z> = PolynomialRing(GF(19))
            sage: I = Ideal([P(0)])
            sage: strat = GroebnerStrategy(I)
            sage: strat == GroebnerStrategy(I)
            True
            sage: I = Ideal([x+1,y+z])
            sage: strat == GroebnerStrategy(I)
            False
        """
        try:
            lx = <GroebnerStrategy?>self
            rx = <GroebnerStrategy?>other
        except TypeError:
            return NotImplemented
        return richcmp(lx._ideal.gens(),
                       rx._ideal.gens(), op)

    def __reduce__(self):
        """
        EXAMPLES::

            sage: from sage.libs.singular.groebner_strategy import GroebnerStrategy
            sage: P.<x,y,z> = PolynomialRing(GF(32003))
            sage: I = Ideal([x + z, y + z])
            sage: strat = GroebnerStrategy(I)
            sage: loads(dumps(strat)) == strat
            True
        """
        return unpickle_GroebnerStrategy0, (self._ideal,)

    cpdef MPolynomial_libsingular normal_form(self, MPolynomial_libsingular p):
        """
        Compute the normal form of ``p`` with respect to the
        generators of this object.

        EXAMPLES::

            sage: from sage.libs.singular.groebner_strategy import GroebnerStrategy
            sage: P.<x,y,z> = PolynomialRing(QQ)
            sage: I = Ideal([x + z, y + z])
            sage: strat = GroebnerStrategy(I)
            sage: strat.normal_form(x*y) # indirect doctest
            z^2
            sage: strat.normal_form(x + 1)
            -z + 1

        TESTS::

            sage: from sage.libs.singular.groebner_strategy import GroebnerStrategy
            sage: P.<x,y,z> = PolynomialRing(QQ)
            sage: I = Ideal([P(0)])
            sage: strat = GroebnerStrategy(I)
            sage: strat.normal_form(x)
            x
            sage: strat.normal_form(P(0))
            0
        """
        if unlikely(p._parent is not self._parent):
            raise TypeError("parent(p) must be the same as this object's parent.")
        if unlikely(self._parent._ring != currRing):
            rChangeCurrRing(self._parent._ring)

        cdef int max_ind = 0
        cdef poly *_p = redNF(p_Copy(p._poly, self._parent._ring), max_ind, 0, self._strat)
        if likely(_p!=NULL):
            _p = redtailBba(_p, max_ind, self._strat)
        return new_MP(self._parent, _p)

cdef class NCGroebnerStrategy(SageObject):
    """
    A Wrapper for Singular's Groebner Strategy Object.

    This object provides functions for normal form computations and
    other functions for Groebner basis computation.

    ALGORITHM:

    Uses Singular via libSINGULAR
    """
    def __init__(self, L):
        """
        Create a new :class:`GroebnerStrategy` object for the
        generators of the ideal ``L``.

        INPUT:

        - ``L`` - an ideal in a g-algebra

        EXAMPLES::

            sage: from sage.libs.singular.groebner_strategy import NCGroebnerStrategy
            sage: A.<x,y,z> = FreeAlgebra(QQ, 3)
            sage: H.<x,y,z> = A.g_algebra({y*x:x*y-z, z*x:x*z+2*x, z*y:y*z-2*y})
            sage: I = H.ideal([y^2, x^2, z^2-H.one()])
            sage: NCGroebnerStrategy(I) #random
            Groebner Strategy for ideal generated by 3 elements over Noncommutative Multivariate Polynomial Ring in x, y, z over Rational Field, nc-relations: {z*x: x*z + 2*x, z*y: y*z - 2*y, y*x: x*y - z}

        TESTS::

            sage: strat = NCGroebnerStrategy(None)
            Traceback (most recent call last):
            ...
            TypeError: First parameter must be an ideal in a g-algebra.

            sage: P.<x,y,z> = PolynomialRing(CC,order='neglex')
            sage: I = Ideal([x+z,y+z+1])
            sage: strat = NCGroebnerStrategy(I)
            Traceback (most recent call last):
            ...
            TypeError:  First parameter must be an ideal in a g-algebra.

        """
        if not isinstance(L, NCPolynomialIdeal):
            raise TypeError("First parameter must be an ideal in a g-algebra.")

        if not isinstance(L.ring(), NCPolynomialRing_plural):
            raise TypeError("First parameter's ring must be a g-algebra.")

        self._ideal = L

        cdef NCPolynomialRing_plural R = <NCPolynomialRing_plural>L.ring()
        self._parent = R
        assert R._ring_ref, "Underlying ring for the Groebner strategy needs to have a refcount"
        self._parent_ring_ref = R._ring_ref
        self._parent_ring = singular_ring_reference(R._ring, self._parent_ring_ref)

        if not R.term_order().is_global():
            raise NotImplementedError("The local case is not implemented yet.")

        if not R.base_ring().is_field():
            raise NotImplementedError("Only coefficient fields are implemented so far.")

        if (R._ring != currRing):
            rChangeCurrRing(R._ring)

        cdef ideal *i = sage_ideal_to_singular_ideal(L)
        self._strat = new_skStrategy()

        self._strat.ak = id_RankFreeModule(i, R._ring)
        #- creating temp data structures
        initBuchMoraCrit(self._strat)
        self._strat.initEcart = initEcartBBA
        self._strat.enterS = enterSBba
        #- set S
        self._strat.sl = -1
        #- init local data struct
        initS(i, NULL, self._strat)

        cdef int j
        if R.base_ring().is_field():
            for j in range(self._strat.sl,-1,-1):
                pNorm(self._strat.S[j])

        id_Delete(&i, R._ring)
        kTest(self._strat)

    def __dealloc__(self):
        """
        TESTS::

            sage: from sage.libs.singular.groebner_strategy import NCGroebnerStrategy
            sage: A.<x,y,z> = FreeAlgebra(QQ, 3)
            sage: H.<x,y,z> = A.g_algebra({y*x:x*y-z, z*x:x*z+2*x, z*y:y*z-2*y})
            sage: I = H.ideal([y^2, x^2, z^2-H.one()])
            sage: strat = NCGroebnerStrategy(I)
            sage: del strat   # indirect doctest
        """
        # WARNING: the Cython class self._parent is no longer accessible!
        # see http://trac.sagemath.org/sage_trac/ticket/11339
        cdef ring *oldRing = NULL
        if self._strat:
            omfree(self._strat.sevS)
            omfree(self._strat.ecartS)
            omfree(self._strat.T)
            omfree(self._strat.sevT)
            omfree(self._strat.R)
            omfree(self._strat.S_2_R)
            omfree(self._strat.L)
            omfree(self._strat.B)
            omfree(self._strat.fromQ)
            id_Delete(&self._strat.Shdl, self._parent._ring)

            if self._parent_ring != currRing:
                oldRing = currRing
                rChangeCurrRing(self._parent_ring)
                delete_skStrategy(self._strat)
                rChangeCurrRing(oldRing)
            else:
                delete_skStrategy(self._strat)
        singular_ring_delete(self._parent_ring, self._parent_ring_ref)

    def _repr_(self):
        """
        TESTS::

            sage: from sage.libs.singular.groebner_strategy import NCGroebnerStrategy
            sage: A.<x,y,z> = FreeAlgebra(QQ, 3)
            sage: H.<x,y,z> = A.g_algebra({y*x:x*y-z, z*x:x*z+2*x, z*y:y*z-2*y})
            sage: I = H.ideal([y^2, x^2, z^2-H.one()])
            sage: strat = NCGroebnerStrategy(I)
            sage: strat # indirect doctest #random
            Groebner Strategy for ideal generated by 3 elements over Noncommutative Multivariate Polynomial Ring in x, y, z over Rational Field, nc-relations: {z*x: x*z + 2*x, z*y: y*z - 2*y, y*x: x*y - z}
        """
        return "Groebner Strategy for ideal generated by %d elements over %s"%(self._ideal.ngens(),self._parent)

    def ideal(self):
        """
        Return the ideal this strategy object is defined for.

        EXAMPLES::

            sage: from sage.libs.singular.groebner_strategy import NCGroebnerStrategy
            sage: A.<x,y,z> = FreeAlgebra(QQ, 3)
            sage: H.<x,y,z> = A.g_algebra({y*x:x*y-z, z*x:x*z+2*x, z*y:y*z-2*y})
            sage: I = H.ideal([y^2, x^2, z^2-H.one()])
            sage: strat = NCGroebnerStrategy(I)
            sage: strat.ideal() == I
            True

        """
        return self._ideal

    def ring(self):
        """
        Return the ring this strategy object is defined over.

        EXAMPLES::

            sage: from sage.libs.singular.groebner_strategy import NCGroebnerStrategy
            sage: A.<x,y,z> = FreeAlgebra(QQ, 3)
            sage: H.<x,y,z> = A.g_algebra({y*x:x*y-z, z*x:x*z+2*x, z*y:y*z-2*y})
            sage: I = H.ideal([y^2, x^2, z^2-H.one()])
            sage: strat = NCGroebnerStrategy(I)
            sage: strat.ring() is H
            True
        """
        return self._parent

    def __richcmp__(self, other, op):
        """
        EXAMPLES::

            sage: from sage.libs.singular.groebner_strategy import NCGroebnerStrategy
            sage: A.<x,y,z> = FreeAlgebra(QQ, 3)
            sage: H.<x,y,z> = A.g_algebra({y*x:x*y-z, z*x:x*z+2*x, z*y:y*z-2*y})
            sage: I = H.ideal([y^2, x^2, z^2-H.one()])
            sage: strat = NCGroebnerStrategy(I)
            sage: strat == NCGroebnerStrategy(I)
            True
            sage: I = H.ideal([y^2, x^2, z^2-H.one()], side='twosided')
            sage: strat == NCGroebnerStrategy(I)
            False
        """
        try:
            lx = <NCGroebnerStrategy?>self
            rx = <NCGroebnerStrategy?>other
        except TypeError:
            return NotImplemented
        return richcmp((lx._ideal.gens(), lx._ideal.side()),
                       (rx._ideal.gens(), rx._ideal.side()), op)

    def __reduce__(self):
        """
        EXAMPLES::

            sage: from sage.libs.singular.groebner_strategy import NCGroebnerStrategy
            sage: A.<x,y,z> = FreeAlgebra(QQ, 3)
            sage: H.<x,y,z> = A.g_algebra({y*x:x*y-z, z*x:x*z+2*x, z*y:y*z-2*y})
            sage: I = H.ideal([y^2, x^2, z^2-H.one()])
            sage: strat = NCGroebnerStrategy(I)
            sage: loads(dumps(strat)) == strat
            True
        """
        return unpickle_NCGroebnerStrategy0, (self._ideal,)

    cpdef NCPolynomial_plural normal_form(self, NCPolynomial_plural p):
        """
        Compute the normal form of ``p`` with respect to the
        generators of this object.

        EXAMPLES::

            sage: A.<x,y,z> = FreeAlgebra(QQ, 3)
            sage: H.<x,y,z> = A.g_algebra({y*x:x*y-z, z*x:x*z+2*x, z*y:y*z-2*y})
            sage: JL = H.ideal([x^3, y^3, z^3 - 4*z])
            sage: JT = H.ideal([x^3, y^3, z^3 - 4*z], side='twosided')
            sage: from sage.libs.singular.groebner_strategy import NCGroebnerStrategy
            sage: SL = NCGroebnerStrategy(JL.std())
            sage: ST = NCGroebnerStrategy(JT.std())
            sage: SL.normal_form(x*y^2)
            x*y^2
            sage: ST.normal_form(x*y^2)
            y*z

        """
        if unlikely(p._parent is not self._parent):
            raise TypeError("parent(p) must be the same as this object's parent.")
        if unlikely(self._parent._ring != currRing):
            rChangeCurrRing(self._parent._ring)

        cdef int max_ind
        cdef poly *_p = redNF(p_Copy(p._poly, self._parent._ring), max_ind, 0, self._strat)
        if likely(_p!=NULL):
            _p = redtailBba(_p, max_ind, self._strat)
        return new_NCP(self._parent, _p)

def unpickle_NCGroebnerStrategy0(I):
    """
    EXAMPLES::

        sage: from sage.libs.singular.groebner_strategy import NCGroebnerStrategy
        sage: A.<x,y,z> = FreeAlgebra(QQ, 3)
        sage: H.<x,y,z> = A.g_algebra({y*x:x*y-z, z*x:x*z+2*x, z*y:y*z-2*y})
        sage: I = H.ideal([y^2, x^2, z^2-H.one()])
        sage: strat = NCGroebnerStrategy(I)
        sage: loads(dumps(strat)) == strat   # indirect doctest
        True
    """
    return NCGroebnerStrategy(I)

def unpickle_GroebnerStrategy0(I):
    """
    EXAMPLES::

        sage: from sage.libs.singular.groebner_strategy import GroebnerStrategy
        sage: P.<x,y,z> = PolynomialRing(GF(32003))
        sage: I = Ideal([x + z, y + z])
        sage: strat = GroebnerStrategy(I)
        sage: loads(dumps(strat)) == strat # indirect doctest
        True
    """
    return GroebnerStrategy(I)
