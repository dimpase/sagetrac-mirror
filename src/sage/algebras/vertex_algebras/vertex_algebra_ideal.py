r"""
Vertex Algebra Ideal

An ideal `I \subset V` of a vertex algebra is a subspace such that

.. MATH::

    a_{(n)} b \in I, \qquad \forall a \in V, b\in I, n \in \mathbb{Z}

The quotient vector space `V/I` is naturally a vertex algebra.

AUTHORS:

- Reimundo Heluani (2019-08-09): Initial implementation.
"""

#******************************************************************************
#       Copyright (C) 2019 Reimundo Heluani <heluani@potuz.net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#                  http://www.gnu.org/licenses/
#*****************************************************************************
from sage.categories.vertex_algebras import VertexAlgebras
from sage.categories.commutative_rings import CommutativeRings
from sage.categories.modules import Modules
from sage.arith.functions import lcm
from sage.combinat.free_module import CombinatorialFreeModule
from sage.structure.unique_representation import UniqueRepresentation
from sage.rings.integer import Integer
from sage.categories.infinite_enumerated_sets import InfiniteEnumeratedSets
from sage.structure.parent import Parent
from sage.modules.with_basis.indexed_element import IndexedFreeModuleElement
from sage.misc.lazy_attribute import lazy_attribute
from sage.rings.all import QQ,NN
from sage.categories.fields import Fields
from sage.structure.element_wrapper import ElementWrapper

class VertexAlgebraIdeal(UniqueRepresentation):
    r"""
    Base class for vertex algebra ideals.

    INPUT:

    - ``ambient`` -- a :mod:`VertexAlgebra`; the ambient vertex
      algebra of this ideal.
      We only support H-graded vertex algebras finitely generated
      by vectors of positive rational conformal weights.

    - ``gens`` -- a tuple or list of elements of ``ambient``; the
      generators of this ideal. We only support ideals generated by
      singular vectors. In addition we require that the subspace of
      ``ambient`` generated by ``gens`` is invariant by the `0`-th
      product action of ``V`` (see the EXAMPLES section below).

    - ``check`` -- a boolean (default: ``True``); whether to check
      that the generators satisfy the conditions described above.

    EXAMPLES::

        sage: V = vertex_algebras.Virasoro(QQ,1/2);V.find_singular(6)
        (L_-2L_-2L_-2|0> + 93/64*L_-3L_-3|0> - 33/8*L_-4L_-2|0> - 27/16*L_-6|0>,)
        sage: v = _[0]; I = V.ideal(v)
        sage: I
        ideal of The Virasoro vertex algebra of central charge 1/2 over Rational Field generated by (L_-2L_-2L_-2|0> + 93/64*L_-3L_-3|0> - 33/8*L_-4L_-2|0> - 27/16*L_-6|0>,)

        sage: V = vertex_algebras.Affine(QQ, 'A1',1, names=('e','h','f'))
        sage: sing = V.find_singular(2); sing
        (e_-1e_-1|0>,
         e_-1h_-1|0> + e_-2|0>,
         h_-1h_-1|0> - 2*e_-1f_-1|0> + h_-2|0>,
         h_-1f_-1|0> + f_-2|0>,
         f_-1f_-1|0>)
        sage: I = V.ideal(sing[0:2])
        Traceback (most recent call last):
        ...
        ValueError: gens must span an invariant subspace of V under 0-th product
        sage: I = V.ideal(sing); I
        ideal of The universal affine vertex algebra of CartanType ['A', 1] at level 1 over Rational Field generated by (e_-1e_-1|0>, e_-1h_-1|0> + e_-2|0>, h_-1h_-1|0> - 2*e_-1f_-1|0> + h_-2|0>, h_-1f_-1|0> + f_-2|0>, f_-1f_-1|0>)

        sage: V = vertex_algebras.Affine(QQ,'A2',3);e = V.gen(0)
        sage: I = V.ideal(e)
        Traceback (most recent call last):
        ...
        ValueError: Generators must be singular vectors of The universal affine vertex algebra of CartanType ['A', 2] at level 3 over Rational Field
    """
    @staticmethod
    def __classcall_private__(cls, ambient=None, *gens, **kwds):
        """
        Vertex algebra ideal classcall.

        EXAMPLES::

            sage: V = vertex_algebras.Affine(QQ,'A1',1)
            sage: sing = V.find_singular(2)
            sage: from sage.algebras.vertex_algebras.vertex_algebra_ideal import VertexAlgebraIdeal
            sage: I = VertexAlgebraIdeal(V,tuple(sing))
            sage: J = VertexAlgebraIdeal(V,[v for v in sing])
            sage: R = VertexAlgebraIdeal(V,sing,check=False)
            sage: I is J
            True
            sage: I is R
            False
        """
        known_keywords = ['check']
        for key in kwds:
            if key not in known_keywords:
                raise TypeError("VertexAlgebraIdeal(): got an unexpected "\
                                "keyword argument '%s'"%key)

        try:
            R = ambient.base_ring()
        except AttributeError:
            R = None

        if R not in CommutativeRings() or ambient not in VertexAlgebras(R):
            raise ValueError("ambient must be a vertex algebra, got {}".format(
                              ambient))

        if len(gens)==0: gens=(ambient.zero(),)

        if isinstance(gens[0], (list, tuple)):
            gens = gens[0]
        gens = [ambient(x) for x in gens if x]
        gens = tuple(gens)

        if ambient in VertexAlgebras(ambient.base_ring()).\
                                Graded().FinitelyGenerated():
            return GradedVertexAlgebraIdeal(ambient, *gens,
                                            check=kwds.get('check',True))

        raise NotImplementedError('Ideals are not implemented for {}'.format(
                                  ambient))

    def __init__(self, ambient, category=None):
        """
        Initialize self.

        TESTS::

            sage: V = vertex_algebras.Virasoro(QQ,1/2)
            sage: I = V.ideal(V.find_singular(6))
            sage: TestSuite(I).run(max_runs=20)  # not tested
        """
        #stick to modules until we have a proper category of modules.
        #or even better of ideals.
        category=Modules(ambient.base_ring()).or_subcategory(category)
        super(VertexAlgebraIdeal,self).__init__(ambient.base_ring(),
                                                category=category)
        self._ambient = ambient

class GradedVertexAlgebraIdeal(VertexAlgebraIdeal,CombinatorialFreeModule):
    r"""
    An ideal of the vertex algebra `V` generated by the list
    of vectors ``gens``.

    INPUT:

    - ``ambient`` -- a :mod:`VertexAlgebra`; the ambient vertex
      algebra of this ideal.
      We only support H-graded vertex algebras finitely generated
      by vectors of positive rational conformal weights.

    - ``gens`` -- a tuple or list of elements of ``ambient``; the
      generators of this ideal. We only support ideals generated by
      singular vectors. In addition we require that the subspace of
      ``ambient`` generated by ``gens`` is invariant by the `0`-th
      product action of ``V`` (see the EXAMPLES section below).

    - ``check`` -- a boolean (default: ``True``); whether to check
      that the generators satisfy the conditions described above.

    EXAMPLES:

    We construct the maximal ideal of the Ising module::

        sage: V = vertex_algebras.Virasoro(QQ,1/2);V.find_singular(6)
        (L_-2L_-2L_-2|0> + 93/64*L_-3L_-3|0> - 33/8*L_-4L_-2|0> - 27/16*L_-6|0>,)
        sage: v = _[0]; I = V.ideal(v)
        sage: I
        ideal of The Virasoro vertex algebra of central charge 1/2 over Rational Field generated by (L_-2L_-2L_-2|0> + 93/64*L_-3L_-3|0> - 33/8*L_-4L_-2|0> - 27/16*L_-6|0>,)

    Generators need to be closed under the `0`-th product::

        sage: V = vertex_algebras.Affine(QQ, 'A1', 1, names=('e', 'h', 'f'))
        sage: sing = V.find_singular(2); sing
        (e_-1e_-1|0>,
         e_-1h_-1|0> + e_-2|0>,
         h_-1h_-1|0> - 2*e_-1f_-1|0> + h_-2|0>,
         h_-1f_-1|0> + f_-2|0>,
         f_-1f_-1|0>)
        sage: V.ideal(sing[0:2])
        Traceback (most recent call last):
        ...
        ValueError: gens must span an invariant subspace of V under 0-th product

    This works if we include all singular vectors of the Affine
    algebra::

        sage: V.ideal(sing)
        ideal of The universal affine vertex algebra of CartanType ['A', 1] at level 1 over Rational Field generated by (e_-1e_-1|0>, e_-1h_-1|0> + e_-2|0>, h_-1h_-1|0> - 2*e_-1f_-1|0> + h_-2|0>, h_-1f_-1|0> + f_-2|0>, f_-1f_-1|0>)

    Generators need to be singular vectors::

        sage: V = vertex_algebras.Affine(QQ,'A1',3);e = V.gen(0)
        sage: I = V.ideal(e)
        Traceback (most recent call last):
        ...
        ValueError: Generators must be singular vectors of The universal affine vertex algebra of CartanType ['A', 1] at level 3 over Rational Field
    """
    def __init__(self, V, *gens, check=True):
        """
        Initialize self.

        TESTS::

            sage: V = vertex_algebras.Virasoro(QQ,1/2)
            sage: I = V.ideal(V.find_singular(6))
            sage: TestSuite(I).run(max_runs=10) # not tested
        """
        if V not in VertexAlgebras(V.base_ring()).Graded().FinitelyGenerated():
            raise ValueError ("V needs to be a finitely generated H-graded"\
                    "vertex algebra, got {}".format(V) )

        if check:
            if any(not g.is_singular() for g in gens):
                raise ValueError ("Generators must be singular vectors of {}"\
                                  .format(V))

            M=V.submodule(gens)
            for v in V.gens():
                if v.weight() in NN:
                    for g in gens:
                        try:
                            M.reduce(v.nmodeproduct(g,0))
                        except ValueError:
                            raise ValueError("gens must span an invariant "\
                                             "subspace of V under 0-th product")

        #TODO: develop vertex-algebra modules to have a right category
        #here
        category = Modules(V.base_ring())
        if V in VertexAlgebras(V.base_ring()).Super():
            category = category.Super()
        category = category.WithBasis().Graded()
        VertexAlgebraIdeal.__init__(self,V,category)
        self._gens = gens
        basis = VertexAlgebraIdealBasis(V,gens)
        CombinatorialFreeModule.__init__(self,V.base_ring(), basis_keys=basis,
                                         category=category,
                                        element_class=VertexAlgebraIdealElement)

        self._unitriangular = bool(V.base_ring() in Fields())
        self.lift.register_as_coercion()

    def lift_on_basis(self,item):
        """
        Lift a basis of the ideal to the ambient space.

        INPUT:

        - ``item`` -- an index of the basis of this ideal

        OUTPUT:

        The element of the ambient vertex algebra indexed by this basis
        index.

        EXAMPLES::

            sage: V = vertex_algebras.Affine(QQ, 'A1',1, names=('e','h','f'))
            sage: sing = V.find_singular(2); sing
            (e_-1e_-1|0>,
             e_-1h_-1|0> + e_-2|0>,
             h_-1h_-1|0> - 2*e_-1f_-1|0> + h_-2|0>,
             h_-1f_-1|0> + f_-2|0>,
             f_-1f_-1|0>)
            sage: I = V.ideal(sing); I
            ideal of The universal affine vertex algebra of CartanType ['A', 1] at level 1 over Rational Field generated by (e_-1e_-1|0>, e_-1h_-1|0> + e_-2|0>, h_-1h_-1|0> - 2*e_-1f_-1|0> + h_-2|0>, h_-1f_-1|0> + f_-2|0>, f_-1f_-1|0>)
            sage: v = I._indices.an_element(); v
            (2, B[0])
            sage: I.lift_on_basis(v)
            e_-1e_-1|0>
        """
        return item.value[1].lift()

    def _repr_(self):
        """
        String representation of this ideal.

        EXAMPLES::

            sage: V = vertex_algebras.Virasoro(QQ,1/2)
            sage: V.ideal(V.find_singular(6))
            ideal of The Virasoro vertex algebra of central charge 1/2 over Rational Field generated by (L_-2L_-2L_-2|0> + 93/64*L_-3L_-3|0> - 33/8*L_-4L_-2|0> - 27/16*L_-6|0>,)
        """
        return "ideal of {0} generated by {1}".format(self._ambient, self._gens)

    def _repr_short(self):
        """
        String representation of this ideal

        EXAMPLES::

            sage: V = vertex_algebras.Virasoro(QQ,1/2);
            sage: I = V.ideal(V.find_singular(6)); I._repr_short()
            'ideal generated by (L_-2L_-2L_-2|0> + 93/64*L_-3L_-3|0> - 33/8*L_-4L_-2|0> - 27/16*L_-6|0>,)'
        """
        return "ideal generated by {}".format(self._gens)

    def _inverse_on_support(self,i):
        """
        The basis index of this element.

        INPUT:

        - ``i`` -- a basis index of the ambient vertex algebra; This
          is a :class:`EnergyPartitionTuple`

        OUTPUT:

        An index of the basis in this ideal or ``None``.

        EXAMPLES::

            sage: V = vertex_algebras.Virasoro(QQ,1/2);
            sage: I = V.ideal(V.find_singular(6));
            sage: idx = V([[1,1,1]]).index()
            sage: I._inverse_on_support(idx)
            (6, B[0])
        """

        M = self.get_weight(i.energy())
        v = M.lift._inverse_on_support(i)
        if v is None:
            return v
        return self._indices((i.energy(),v))

    @lazy_attribute
    def lift(self):
        """
        The embedding of this ideal into its ambient vertex algebra.

        EXAMPLES::

            sage: V = vertex_algebras.Virasoro(QQ,1/2);
            sage: I = V.ideal(V.find_singular(6));
            sage: I.lift
            Generic morphism:
              From: ideal of The Virasoro vertex algebra of central charge 1/2 over Rational Field generated by (L_-2L_-2L_-2|0> + 93/64*L_-3L_-3|0> - 33/8*L_-4L_-2|0> - 27/16*L_-6|0>,)
              To:   The Virasoro vertex algebra of central charge 1/2 over Rational Field
        """
        key = self._ambient.basis().keys().rank
        return self.module_morphism(self.lift_on_basis,
                                    codomain=self._ambient,
                                    triangular="lower",
                                    unitriangular=self._unitriangular,
                                    key=key,
                                    inverse_on_support=self._inverse_on_support)

    def get_weight(self,n):
        r"""
        The homogeneous component of weight ``n`` in this ideal.

        INPUT:

        - ``n`` -- a non-negative rational number

        OUTPUT:

        A subspace of the ambient vertex algebra of this ideal
        given as the intersection of the conformal weight ``n`` of
        the vertex algebra with this ideal.

        EXAMPLES::

            sage: V = vertex_algebras.Virasoro(QQ,1/2); I = V.ideal(V.find_singular(6))
            sage: I.get_weight(6)
            Free module generated by {0} over Rational Field
            sage: I.get_weight(6).an_element().lift()
            2*L_-2L_-2L_-2|0> + 93/32*L_-3L_-3|0> - 33/4*L_-4L_-2|0> - 27/8*L_-6|0>
            sage: M = I.get_weight(7); M
            Free module generated by {0} over Rational Field
            sage: M.reduce(I.gens()[0].T())
            0
            sage: V = vertex_algebras.Affine(QQ,'A1',1); V.register_lift()
            sage: I = V.ideal(V.find_singular(2))
            sage: I
            ideal of The universal affine vertex algebra of CartanType ['A', 1] at level 1 over Rational Field generated by (E(alpha[1])_-1E(alpha[1])_-1|0>, E(alpha[1])_-1E(alphacheck[1])_-1|0> + E(alpha[1])_-2|0>, E(alphacheck[1])_-1E(alphacheck[1])_-1|0> - 2*E(alpha[1])_-1E(-alpha[1])_-1|0> + E(alphacheck[1])_-2|0>, E(alphacheck[1])_-1E(-alpha[1])_-1|0> + E(-alpha[1])_-2|0>, E(-alpha[1])_-1E(-alpha[1])_-1|0>)
            sage: I.get_weight(3)
            Free module generated by {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14} over Rational Field
        """
        return self._indices.get_weight(n)

    def get_weight_less_than(self,n):
        """
        The subspace of vectors of conformal weight less than ``n`` in
        this ideal.

        INPUT:

        - ``n`` -- a non-negative rational number

        EXAMPLES::

            sage: V = vertex_algebras.Virasoro(QQ,1/2); I = V.ideal(V.find_singular(6))
            sage: I.get_weight_less_than(7)
            Free module generated by {0} over Rational Field
            sage: M = I.get_weight_less_than(9); M
            Free module generated by {0, 1, 2, 3} over Rational Field
            sage: M.an_element().lift()
            2*L_-2L_-2L_-2|0> + 93/32*L_-3L_-3|0> - 33/4*L_-4L_-2|0> - 27/8*L_-6|0> + 2*L_-3L_-2L_-2|0> + 9/8*L_-4L_-3|0> - 25/4*L_-5L_-2|0> - 27/16*L_-7|0> + 3*L_-2L_-2L_-2L_-2|0> - 1071/64*L_-4L_-2L_-2|0> - 2511/1024*L_-4L_-4|0> + 19809/2048*L_-5L_-3|0> - 657/256*L_-6L_-2|0> - 9945/2048*L_-8|0>
            sage: I.get_weight_less_than(6)
            Free module generated by {} over Rational Field
        """
        if n not in QQ or n < 0:
            raise ValueError("n must be a positive rational number")

        basis = []
        for i in self._indices:
            if i.value[0] < n:
                basis.append(i.value[1].lift())
            else:
                break
        return self._ambient.submodule(basis)

    def ambient(self):
        """
        The ambient vertex algebra of this ideal.

        EXAMPLES::

            sage: V = vertex_algebras.Virasoro(QQ,1/2); v = V.find_singular(6)[0]; I = V.ideal(v); I
            ideal of The Virasoro vertex algebra of central charge 1/2 over Rational Field generated by (L_-2L_-2L_-2|0> + 93/64*L_-3L_-3|0> - 33/8*L_-4L_-2|0> - 27/16*L_-6|0>,)
            sage: I.ambient()
            The Virasoro vertex algebra of central charge 1/2 over Rational Field
        """
        return self._ambient

    def reduce(self,x):
        """
        The reduction of ``x`` modulo this ideal.

        INPUT:

        - ``x`` -- an element of the ambient vertex algebra

        EXAMPLES::

            sage: V = vertex_algebras.Virasoro(QQ,1/2); I = V.ideal(V.find_singular(6)); I
            ideal of The Virasoro vertex algebra of central charge 1/2 over Rational Field generated by (L_-2L_-2L_-2|0> + 93/64*L_-3L_-3|0> - 33/8*L_-4L_-2|0> - 27/16*L_-6|0>,)
            sage: L = V.0; I.reduce(L*(L*L))
            -93/64*L_-3L_-3|0> + 33/8*L_-4L_-2|0> + 27/16*L_-6|0>
            sage: I.reduce(L+L.T())
            L_-2|0> + L_-3|0>
        """
        if x.is_zero():
            return x
        if x.is_homogeneous():
            w = x.weight()
            I = self.get_weight(w)
            A = self._ambient.get_weight(w)
            M = A.submodule([A.retract(v.lift()) for v in I.basis()])
            return M.reduce(A.retract(x)).lift()
        return sum(self.reduce(m) for m in x.homogeneous_terms())

    def __contains__(self,x):
        """
        Whether ``x`` is in this ideal.

        INPUT:

        - ``x`` -- an element of the ambient vertex algebra or of this
          ideal

        EXAMPLES::

            sage: V = vertex_algebras.NeveuSchwarz(QQ,7/10)
            sage: v = V.find_singular(4)[0]
            sage: v
            L_-2L_-2|0> - 3/2*G_-5/2G_-3/2|0> + 3/10*L_-4|0>
            sage: I = V.ideal(v)
            sage: v.T() in I
            True
            sage: w = I.an_element(); w
            L_-2L_-2|0> - 3/2*G_-5/2G_-3/2|0> + 3/10*L_-4|0> + 3*L_-3L_-2|0> - 9/2*G_-7/2G_-3/2|0> + 3/5*L_-5|0> + 5*L_-2L_-2G_-3/2|0> + 63/2*L_-4G_-3/2|0> - 65*L_-2G_-7/2|0> + 287/2*G_-11/2|0>
            sage: w in I
            True
        """
        if super(GradedVertexAlgebraIdeal,self).__contains__(x):
            return True
        if x in self._ambient:
            return not self.reduce(x)
        return False

    def _an_element_(self):
        """
        An element of this ideal.

        EXAMPLES::

            sage: V = vertex_algebras.NeveuSchwarz(QQ,7/10)
            sage: I = V.ideal(V.find_singular(4));
            sage: I.an_element()
            L_-2L_-2|0> - 3/2*G_-5/2G_-3/2|0> + 3/10*L_-4|0> + 3*L_-3L_-2|0> - 9/2*G_-7/2G_-3/2|0> + 3/5*L_-5|0> + 5*L_-2L_-2G_-3/2|0> + 63/2*L_-4G_-3/2|0> - 65*L_-2G_-7/2|0> + 287/2*G_-11/2|0>
        """
        B = self.basis()
        return B[self._indices[0]] + 3*B[self._indices[2]] + 5*B[self._indices[3]]

    def gens(self):
        """
        The generators of this ideal.

        EXAMPLES::

            sage: V = vertex_algebras.Affine(QQ,'A1',1, names = ('e','h','f'));
            sage: I = V.ideal(V.find_singular(2))
            sage: I.gens()
            (e_-1e_-1|0>,
             e_-1h_-1|0> + e_-2|0>,
             h_-1h_-1|0> - 2*e_-1f_-1|0> + h_-2|0>,
             h_-1f_-1|0> + f_-2|0>,
             f_-1f_-1|0>)
        """
        return self._gens

class VertexAlgebraIdealElement(IndexedFreeModuleElement):
    """
    Base class for elements in a vertex algebra ideal.
    """
    def _repr_(self):
        """
        String representation of this element.

        EXAMPLES::

            sage: V = vertex_algebras.NeveuSchwarz(QQ,7/10)
            sage: I = V.ideal(V.find_singular(4)); B = I.basis()
            sage: B[I._indices[0]]
            L_-2L_-2|0> - 3/2*G_-5/2G_-3/2|0> + 3/10*L_-4|0>
        """
        return repr(self.lift())

    def lift(self):
        """
        This element in the ambient vertex algebra.

        EXAMPLES::

            sage: V = vertex_algebras.NeveuSchwarz(QQ,7/10)
            sage: I = V.ideal(V.find_singular(4)); v = I.an_element()
            sage: v.parent()
            ideal of The Neveu-Schwarz super vertex algebra of central charge 7/10 over Rational Field generated by (L_-2L_-2|0> - 3/2*G_-5/2G_-3/2|0> + 3/10*L_-4|0>,)
            sage: w = v.lift(); w
            L_-2L_-2|0> - 3/2*G_-5/2G_-3/2|0> + 3/10*L_-4|0> + 3*L_-3L_-2|0> - 9/2*G_-7/2G_-3/2|0> + 3/5*L_-5|0> + 5*L_-2L_-2G_-3/2|0> + 63/2*L_-4G_-3/2|0> - 65*L_-2G_-7/2|0> + 287/2*G_-11/2|0>
            sage: w.parent()
            The Neveu-Schwarz super vertex algebra of central charge 7/10 over Rational Field
        """
        return self.parent().lift(self)

class VertexAlgebraIdealBasis(Parent):
    """
    A basis for a vertex algebra ideal.

    This class implements the necessary methods to construct an
    infinite dimensional submodule of a vertex algebra (which itself
    is an infinite dimensional module) as well as to construct the
    corresponding quotient.

    INPUT:

    - ``V`` -- a :class:`VertexAlgebra`; the ambient of the ideal
    - ``gens`` -- a list or tuple of elements in ``V``; the
      generators of the ideal

    EXAMPLES::

        sage: V = vertex_algebras.Virasoro(QQ,1/2)
        sage: I = V.ideal(V.find_singular(6))
        sage: I._indices
        Basis of the vertex algebra ideal of The Virasoro vertex algebra of central charge 1/2 over Rational Field generated by (L_-2L_-2L_-2|0> + 93/64*L_-3L_-3|0> - 33/8*L_-4L_-2|0> - 27/16*L_-6|0>,)
    """
    def __init__(self,V,gens):
        """
        Initialize self.

        EXAMPLES::

            sage: V = vertex_algebras.Virasoro(QQ,1/2)
            sage: I = V.ideal(V.find_singular(6))
            sage: J = I._indices
            sage: TestSuite(J).run(max_run=10) # not tested
        """
        self._ambient = V
        self._gens = gens
        Parent.__init__(self, category=InfiniteEnumeratedSets())

    def _repr_(self):
        """
        The name of this class.

        EXAMPLES::

            sage: V = vertex_algebras.NeveuSchwarz(QQ,7/10)
    sage: I = V.ideal(V.find_singular(4)); I._indices
    Basis of the vertex algebra ideal of The Neveu-Schwarz super vertex algebra of central charge 7/10 over Rational Field generated by (L_-2L_-2|0> - 3/2*G_-5/2G_-3/2|0> + 3/10*L_-4|0>,)
        """
        return "Basis of the vertex algebra ideal of {} generated by {}".format(
            self._ambient,self._gens)

    def _element_constructor_(self,x):
        """
        Construct an element in this basis.

        INPUT:

        - ``x`` -- a pair ``(k,v)`` where ``k`` is a non-negative
          rational number (the degree of this vector) and ``v`` is
          either a basis index of the space of conformal weight ``k``
          as returned by :meth:`get_weight` or a basis element.

        EXAMPLES::

            sage: V = vertex_algebras.NeveuSchwarz(QQ,7/10)
            sage: I = V.ideal(V.find_singular(4));
            sage: B = I._indices
            sage: B([5,0])
            (5, B[0])
            sage: M = I.get_weight(5)
            sage: R = M.basis()
            sage: B([5,R[0]])
            (5, B[0])
        """
        if not isinstance(x,(tuple,list)) or len(x) != 2:
            raise ValueError("Do not know how to convert {} into {}".format(x,
                             self))
        if x[0] not in QQ or x[0] < 0:
            raise ValueError("Do not know how to convert {} into {}".format(x,
                             self))
        B = self.get_weight(x[0]).basis()
        if x[1] in B.keys():
            return self.element_class(self,(x[0],B[x[1]]))
        if x[1] in B:
            return self.element_class(self,tuple(x))
        raise ValueError("Do not know how to convert {} into {}".format(x,self))

    class Element(ElementWrapper):
        pass

    def __iter__(self):
        """
        Iterate over all basis elements.

        EXAMPLES::

            sage: V = vertex_algebras.Virasoro(QQ,1/2); I = V.ideal(V.find_singular(6))
            sage: I._indices[0:10]  # long time (2 seconds)
            [(6, B[0]),
             (7, B[0]),
             (8, B[0]),
             (8, B[1]),
             (9, B[0]),
             (9, B[1]),
             (9, B[2]),
             (10, B[0]),
             (10, B[1]),
             (10, B[2])]
        """
        vgens = self._ambient.gens()
        weights = [g.degree() for g in vgens]
        step = lcm([w.denominator() for w in weights])
        n = 0
        while True:
            M = self.get_weight(n/step)
            for y in M.basis():
                yield self.element_class(self,(n/step,y))
            n += 1

    def get_weight(self,n):
        """
        The subspace of conformal weight ``n``.

        INPUT:

        - ``n`` -- a non-negative rational number.

        OUTPUT:

        The subspace of the ambient vertex algebra generated by all
        vectors of energy ``n`` in this basis.

        EXAMPLES::

            sage: V = vertex_algebras.Virasoro(QQ,1/2); I = V.ideal(V.find_singular(6))
            sage: I._indices.get_weight(9)
            Free module generated by {0, 1, 2} over Rational Field
        """
        vgens = self._ambient.gens()
        weights = [g.degree() for g in vgens]
        regular = [2*g.is_even_odd() for g in vgens]
        # Do we need to add T(g) here if the Vertex algebra is not
        # conformal?
        basis = [g._action_from_partition_tuple(pt) for g in self._gens if\
                 n-g.weight() >= 0 for pt in _negative_pt(weights,regular,
                 n-g.weight())]
        return self._ambient.submodule(basis)

    def __getitem__(self,r):
        """
        List elements in this basis.

        EXAMPLES::

            sage: V = vertex_algebras.Virasoro(QQ,1/2); I = V.ideal(V.find_singular(6))
            sage: I._indices[4]         # long time (1 second)
            (9, B[0])
            sage: I._indices[2:4]       # long time (1 second)
            [(8, B[0]), (8, B[1])]
        """
        if isinstance(r,self.element_class):
            return r
        if isinstance(r,(int,Integer)):
            return self.unrank(r)
        elif isinstance(r,slice):
            start=0 if r.start is None else r.start
            stop=r.stop
            if stop is None:
                raise ValueError('infinite set')
            count=0
            parts=[]
            for t in self:
                if count==stop:
                    break
                if count>=start:
                    parts.append(t)
                count+=1
            if count==stop or stop is None:
                return parts
            raise IndexError('value out of range')
        raise NotImplementedError('Do not know how to look for {}'.format(r))

def _negative_pt(weights,regular,energy=None):
    """
    helper function to compute tuples of shifted modes.

    These are to be fed into
    :meth:`algebras.lie_conformal_algebras.lie_conformal_algebra_element._action_from_partition_tuple`

    EXAMPLES::

        sage: from sage.algebras.vertex_algebras.vertex_algebra_ideal import _negative_pt
        sage: [p for p in _negative_pt((2,3/2),(0,2),5/2)]
        [([1, 1], [1/2]), ([2], [1/2]), ([1], [3/2]), ([], [5/2])]
        sage: [p for p in _negative_pt((2,3/2),(0,2),0)]
        [([], [])]
        sage: L = _negative_pt((2,3/2),(0,2))
        sage: [next(L) for i in range(8)]
        [([], []),
         ([], [1/2]),
         ([1], []),
         ([1], [1/2]),
         ([], [3/2]),
         ([1, 1], []),
         ([2], []),
         ([], [3/2, 1/2])]
    """
    from sage.arith.misc import integer_floor
    from .energy_partition_tuples import EnergyPartitionTuples
    newwgts = [w-integer_floor(w) for w in weights]
    newwgts = [w if w else w+1 for w in newwgts]
    if energy is not None:
        from sage.rings.rational_field import QQ
        if energy not in QQ or energy < 0:
            raise ValueError("energy needs to be a non-negative rational")

        EPT = EnergyPartitionTuples(newwgts,len(weights),energy,regular=regular)
    else:
        EPT = EnergyPartitionTuples(newwgts,len(weights),regular=regular)

    for p in EPT:
        modp = p.to_list()
        modp = [[part + w -1 for part in l] for l,w in zip(modp,newwgts)]
        yield tuple(modp)

    def is_submodule(self,other):
        if other is self._ambient or other is self:
            return True
        raise NotImplementedError()
