r"""
Poisson Vertex Algebra Ideal

Given a (super) Poisson vertex algebra `P`. An ideal `I \subset P` is a
subspace which is both an ideal of the (super) commutative ring
`(P,\cdot)` and an ideal of the (super) Lie conformal algebra
`(P,\{ \cdot_\lambda \cdot \}, T)`.

AUTHORS:

- Reimundo Heluani (2020-06-15): Initial implementation.
"""

#******************************************************************************
#       Copyright (C) 2020 Reimundo Heluani <heluani@potuz.net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#                  http://www.gnu.org/licenses/
#*****************************************************************************
from sage.structure.unique_representation import UniqueRepresentation
from sage.categories.commutative_rings import CommutativeRings
from sage.categories.poisson_vertex_algebras import PoissonVertexAlgebras
from sage.categories.infinite_enumerated_sets import InfiniteEnumeratedSets
from sage.combinat.free_module import CombinatorialFreeModule
from sage.structure.parent import Parent
from sage.modules.with_basis.indexed_element import IndexedFreeModuleElement
from sage.misc.lazy_attribute import lazy_attribute
from sage.arith.functions import lcm
from sage.categories.modules import Modules
from sage.rings.all import QQ, ZZ
from sage.categories.fields import Fields
from sage.structure.element_wrapper import ElementWrapper
from sage.rings.integer import Integer
from sage.functions.other import floor

class PoissonVertexAlgebraIdeal(UniqueRepresentation):
    """
    Base class for vertex algebra ideals.

    INPUT:

    - ``ambient`` -- a Poisson vertex algebra; the ambient of this
      ideal. We only support H-graded Poisson vertex algebras finitely
      generated by vectors of positive rational conformal weights.

    - ``gens`` a list or tuple of elements of ``ambient``; the
      generators of this ideal. We only support ideals generated by
      singular vectors

    In addition the following keywords are recognized:

    - ``check`` -- a boolean (default: ``True``): whether to check
      that the generators are singular.

    .. NOTE::

        This class is not meant to be called directly by the user but
        rather the user should call
        :meth:`~sage.categories.poisson_vertex_algebras.PoissonVertexAlgebras.ParentMethods.ideal`.

    EXAMPLES::

        sage: V = vertex_algebras.Affine(QQ, 'A1', 1, names=('e','h','f'))
        sage: P = V.classical_limit()
        sage: sing = V.find_singular(2); sing
        (e_-1e_-1|0>,
         e_-1h_-1|0> + e_-2|0>,
         h_-1h_-1|0> - 2*e_-1f_-1|0> + h_-2|0>,
         h_-1f_-1|0> + f_-2|0>,
         f_-1f_-1|0>)
        sage: gens = [P(v).li_filtration_lt() for v in sing]; gens
        [e_1^2, e_1*h_1, h_1^2 - 2*e_1*f_1, h_1*f_1, f_1^2]
        sage: I = P.ideal(gens); I
        ideal of The classical limit of The universal affine vertex algebra of CartanType ['A', 1] at level 1 over Rational Field generated by (e_1^2, e_1*h_1, h_1^2 - 2*e_1*f_1, h_1*f_1, f_1^2)
        sage: R = P.quotient(I)
        sage: Q = V.quotient(V.ideal(sing)); Q
        Quotient of The universal affine vertex algebra of CartanType ['A', 1] at level 1 over Rational Field by the ideal generated by (e_-1e_-1|0>, e_-1h_-1|0> + e_-2|0>, h_-1h_-1|0> - 2*e_-1f_-1|0> + h_-2|0>, h_-1f_-1|0> + f_-2|0>, f_-1f_-1|0>)
        sage: Q.arc_algebra() is R
        True
    """
    @staticmethod
    def __classcall_private__(cls, ambient=None, *gens, **kwds):
        """
        Poisson vertex algebra ideal classcall.

        EXAMPLES::

            sage: V = vertex_algebras.Affine(QQ, 'A1', 1, names=('e','h','f'))
            sage: P = V.classical_limit()
            sage: sing = V.find_singular(2)
            sage: gens = [P(v).li_filtration_lt() for v in sing]
            sage: I = P.ideal(gens)
            sage: from sage.algebras.poisson_vertex_algebras.poisson_vertex_algebra_ideal import PoissonVertexAlgebraIdeal
            sage: J = PoissonVertexAlgebraIdeal(P, tuple(gens))
            sage: J is I
            True
        """
        known_keywords = ['check']
        for key in kwds:
            if key not in known_keywords:
                raise TypeError("PoissonVertexAlgebraIdeal(): got an "
                                "unexpected keyword argument '%s'"%key)
        try:
            R = ambient.base_ring()
        except AttributeError:
            R = None

        if R not in CommutativeRings() or\
            ambient not in PoissonVertexAlgebras(R):
            raise ValueError("ambient must be a Poisson vertex algebra, got {}"\
                            .format(ambient))

        if len(gens) == 0: gens=(ambient.zero(),)

        if isinstance(gens[0], (list, tuple)):
            gens = gens[0]
        gens = [ambient(x) for x in gens if x]
        gens = tuple(gens)
        if len(gens)==0: gens=(ambient.zero(),)

        if ambient in PoissonVertexAlgebras(ambient.base_ring()).\
                                Graded().FinitelyGenerated():
            return GradedPoissonVertexAlgebraIdeal(ambient, *gens,
                                                   check=kwds.get('check',True))

        raise NotImplementedError('Ideals are not implemented for {}'.format(
                                  ambient))

    def __init__(self, ambient, category=None):
        """
        Initialize self.

        TESTS::

            sage: V = vertex_algebras.Affine(QQ, 'A1', 1, names=('e','h','f'))
            sage: P = V.classical_limit()
            sage: sing = V.find_singular(2)
            sage: gens = [P(v).li_filtration_lt() for v in sing]
            sage: I = P.ideal(gens);
            sage: TestSuite(I).run()    # not tested
        """
        #stick to modules until we have a proper category of modules.
        #or even better of ideals.
        category=Modules(ambient.base_ring()).or_subcategory(category)
        super(PoissonVertexAlgebraIdeal,self).__init__(ambient.base_ring(),
                                                       category=category)
        self._ambient = ambient

class GradedPoissonVertexAlgebraIdeal(PoissonVertexAlgebraIdeal,
                                      CombinatorialFreeModule):
    r"""
    An ideal of the Poisson vertex algebra `V` generated by the
    list of vectors ``gens``.

    INPUT:

    - ``V`` -- a Poisson vertex algebra; the ambient of this ideal.
      We only support H-graded vertex algebras finitely generated
      by vectors of positive rational conformal weights.

    - ``gens`` a tuple of homogeneous elements of ``V``; the
      generators of this ideal. We only support ideals such that
      the `R`-submodule `M \subset V` generated by ``gens``
      satisfies the following two conditions for every generator
      `g` of `V`:

      1. `g_{(n)} M = 0` for `n>0`,
      2. `g_{(0)} M \subset M`.

    - ``check`` -- a boolean (default: ``True``); whether to check
      that the generators satisfy the condition above.

    EXAMPLES::

        sage: V = vertex_algebras.Abelian(QQ, 4);
        sage: P = V.classical_limit()
        sage: P
        The classical limit of The Abelian vertex algebra over Rational Field with generators (a0_-1|0>, a1_-1|0>, a2_-1|0>, a3_-1|0>)
        sage: P.inject_variables()
        Defining a0, a1, a2, a3
        sage: I = P.ideal(a0**3+a1*a2*a3); I
        ideal of The classical limit of The Abelian vertex algebra over Rational Field with generators (a0_-1|0>, a1_-1|0>, a2_-1|0>, a3_-1|0>) generated by (a0_1^3 + a1_1*a2_1*a3_1,)
        sage: I.hilbert_series(8)
        1 + 4*q + 14*q^2 + 39*q^3 + 100*q^4 + 233*q^5 + 515*q^6 + 1077*q^7 + O(q^8)
    """
    def __init__(self, V, *gens, check=True):
        """
        Initialize self.

        EXAMPLES::

            sage: V = vertex_algebras.Abelian(QQ, 4);
            sage: P = V.classical_limit()
            sage: P.inject_variables()
            Defining a0, a1, a2, a3
            sage: I = P.ideal(a0**3+a1*a2*a3)
            sage: TestSuite(I).run()    # not tested
        """
        if V not in PoissonVertexAlgebras(V.base_ring()).Graded()\
            .FinitelyGenerated():
            raise ValueError ("V needs to be a finitely generated H-graded "\
                    "Poisson vertex algebra, got {}".format(V))

        if check:
                M = V.submodule(gens)
                for g in V.gens():
                    for b in gens:
                        if not b.is_homogeneous():
                            raise ValueError("generators need to be "\
                                             "homogeneous, got {}".format(b))
                        br = g._bracket_(b)
                        try:
                            M.reduce(br.pop(0,V.zero()))
                        except ValueError:
                            raise ValueError("generators must be stable "\
                                "under the zeroth product")
                        if br:
                            raise ValueError("{}{}{}".format(g,b,br))
                            raise ValueError("generators must be singular"\
                                             "vectors of {}".format(V))

        category = Modules(V.base_ring())
        if V in PoissonVertexAlgebras(V.base_ring()).Super():
            category = category.Super()
        category = category.WithBasis().Graded()
        PoissonVertexAlgebraIdeal.__init__(self, V, category)
        self._gens = gens
        basis = PoissonVertexAlgebraIdealBasis(V, gens)
        CombinatorialFreeModule.__init__(self, V.base_ring(),
                                basis_keys=basis, category=category,
                                element_class=PoissonVertexAlgebraIdealElement)

        self._unitriangular = bool(V.base_ring() in Fields())
        self.lift.register_as_coercion()
        self.coerce_embedding = self.lift

    def lift_on_basis(self,item):
        """
        Lift a basis of the ideal to the ambient space.

        INPUT:

        - ``item`` -- an index of the basis of this ideal

        OUTPUT:

        The element of the ambient Poisson vertex algebra indexed by
        this basis index.

        EXAMPLES::

            sage: V = vertex_algebras.Affine(QQ, 'A1',1, names=('e','h','f'))
            sage: Q = V.quotient(V.ideal(V.find_singular(2)))
            sage: P = Q.arc_algebra()
            sage: I = P.defining_ideal(); I
            ideal of The classical limit of The universal affine vertex algebra of CartanType ['A', 1] at level 1 over Rational Field generated by (e_1^2, e_1*h_1, h_1^2 - 2*e_1*f_1, h_1*f_1, f_1^2)
            sage: v = I._indices.an_element(); v
            (2, B[0])
            sage: I.lift_on_basis(v)
            e_1^2
        """
        return item.value[1].lift()

    def _repr_(self):
        """
        String representation of this ideal.

        EXAMPLES::

            sage: V = vertex_algebras.NeveuSchwarz(QQ,1);
            sage: P = V.classical_limit()
            sage: P.inject_variables()
            Defining L, G
            sage: I = P.ideal(L**2); I
            ideal of The classical limit of The Neveu-Schwarz super vertex algebra of central charge 1 over Rational Field generated by (L_2^2,)
        """
        return "ideal of {} generated by {}".format(self._ambient, self._gens)

    def _repr_short(self):
        """
        String representation of this ideal.

        EXAMPLES::

            sage: V = vertex_algebras.NeveuSchwarz(QQ,1);
            sage: P = V.classical_limit()
            sage: P.inject_variables()
            Defining L, G
            sage: I = P.ideal(L**2); I
            ideal of The classical limit of The Neveu-Schwarz super vertex algebra of central charge 1 over Rational Field generated by (L_2^2,)
        """
        return "the ideal generated by {}".format(self._gens)

    def _inverse_on_support(self,i):
        """
        The basis index of this element.

        INPUT:

        - ``i`` -- a basis index of the ambient Poisson vertex algebra;
          This is a :class:`EnergyPartitionTuple`

        OUTPUT:

        An index of the basis in this ideal or ``None``.

        EXAMPLES::

            sage: V = vertex_algebras.NeveuSchwarz(QQ, 7/10)
            sage: Q = V.quotient(V.ideal(V.find_singular(4)))
            sage: P = Q.arc_algebra(); I = P.defining_ideal()
            sage: R = V.classical_limit()
            sage: v = R([[2,1,1],[1]]); v
            L_3*L_2^2*G_3/2
            sage: I._inverse_on_support(v.index())
            (17/2, B[0])
        """
        M = self.get_weight(i.energy())
        v = M.lift._inverse_on_support(i)
        if v is None:
            return v
        return self._indices((i.energy(),v))

    @lazy_attribute
    def lift(self):
        """
        The embedding of this ideal into its ambient Poisson vertex
        algebra.

        EXAMPLES::

            sage: V = vertex_algebras.NeveuSchwarz(QQ, 7/10)
            sage: Q = V.quotient(V.ideal(V.find_singular(4)))
            sage: P = Q.arc_algebra(); I = P.defining_ideal()
            sage: I.lift
            Generic morphism:
              From: ideal of The classical limit of The Neveu-Schwarz super vertex algebra of central charge 7/10 over Rational Field generated by (L_2^2,)
              To:   The classical limit of The Neveu-Schwarz super vertex algebra of central charge 7/10 over Rational Field
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
        The homogeneous component of weight ``n`` in the ideal.

        INPUT:

        - ``n`` -- a non-negative rational number

        OUTPUT:

        A subspace of the ambient Poisson vertex algebra of
        this ideal given as the intersection of the conformal weight
        ``n`` of the Poisson vertex algebra with this ideal.

        EXAMPLES::

            sage: V = vertex_algebras.Affine(QQ,'A1', 2, names = ('e','f','h'));
            sage: Q = V.quotient(V.ideal(V.find_singular(3)))
            sage: P = Q.arc_algebra()
            sage: I = P.defining_ideal()
            sage: M = I.get_weight(4); M
            Free module generated by {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20} over Rational Field
            sage: v = M.an_element(); v
            2*B[0] + 2*B[1] + 3*B[2]
            sage: v.lift()
            2*e_1^4 + 2*e_1^3*f_1 + 3*e_1^2*f_1^2
        """
        return self._indices.get_weight(n)

    def get_weight_less_than(self,n):
        """
        The subspace of vectors of conformal weight less than
        ``n`` in this ideal.

        INPUT:

        - ``n`` -- a non-negative rational number

        EXAMPLES::

            sage: V = vertex_algebras.Abelian(QQ, 4)
            sage: P = V.classical_limit(); P.inject_variables()
            Defining a0, a1, a2, a3
            sage: I = P.ideal(a0**3-a1*a2*a3)
            sage: M = I.get_weight_less_than(5); M
            Free module generated by {0, 1, 2, 3, 4, 5} over Rational Field
            sage: M.an_element().lift()
            2*a0_1^3 - 2*a1_1*a2_1*a3_1 + 2*a0_1^4 + 3*a0_1^3*a1_1 - 2*a0_1*a1_1*a2_1*a3_1 - 3*a1_1^2*a2_1*a3_1
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
        The ambient Poisson vertex algebra of this ideal.

        EXAMPLES::

            sage: V = vertex_algebras.Affine(QQ,'A1', 2, names = ('e','f','h'));
            sage: Q = V.quotient(V.ideal(V.find_singular(3)))
            sage: P = Q.arc_algebra(); I = P.defining_ideal()
            sage: I.ambient()
            The classical limit of The universal affine vertex algebra of CartanType ['A', 1] at level 2 over Rational Field
        """
        return self._ambient

    def reduce(self,x):
        """
        The reduction of ``x`` modulo this ideal.

        INPUT:

        - ``x`` -- an element of the ambient Poisson vertex algebra.

        EXAMPLES::

            sage: V = vertex_algebras.Virasoro(QQ, 1/2);
            sage: Q = V.quotient(V.ideal(V.find_singular(6)))
            sage: P = V.classical_limit(); R = Q.arc_algebra()
            sage: I = R.defining_ideal()
            sage: v = P([[1,1,1]])+3*P([[3,1]]); v
            L_2^3 + 3*L_4*L_2
            sage: I.reduce(v)
            3*L_4*L_2
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
        Whether this Poisson vertex algebra contains this element.

        EXAMPLES::

            sage: V = vertex_algebras.Virasoro(QQ, 1/2);
            sage: Q = V.quotient(V.ideal(V.find_singular(6)))
            sage: P = V.classical_limit(); R = Q.arc_algebra()
            sage: I = R.defining_ideal()
            sage: v = P.an_element(); v
            1 + 2*L_2 + 3*L_3 + L_2^4
            sage: v in I
            False
            sage: P.inject_variables()
            Defining L
            sage: w = (L**3).T(5); w
            360*L_4^2*L_3 + 360*L_5*L_3^2 + 720*L_5*L_4*L_2 + 720*L_6*L_3*L_2 + 360*L_7*L_2^2
            sage: w in I
            True
        """
        if super(GradedPoissonVertexAlgebraIdeal,self).__contains__(x):
            return True
        if x in self._ambient:
            return not self.reduce(x)
        return False

    def _an_element_(self):
        """
        An element of this ideal.

        EXAMPLES::

            sage: V = vertex_algebras.Virasoro(QQ, 1/2);
            sage: Q = V.quotient(V.ideal(V.find_singular(6)))
            sage: R = Q.arc_algebra()
            sage: I = R.defining_ideal()
            sage: I.an_element()
            L_2^3 + 3*L_2^4 + 5*L_3^2*L_2 + 5*L_4*L_2^2
        """
        B = self.basis()
        return B[self._indices[0]] + 3*B[self._indices[2]] + 5*B[self._indices[3]]

    def gens(self):
        """
        The generators of this ideal.

        EXAMPLES::

            sage: V = vertex_algebras.Affine(QQ,'A1', 1, names = ('e','f','h'));
            sage: Q = V.quotient(V.ideal(V.find_singular(2)))
            sage: R = Q.arc_algebra(); I = R.defining_ideal()
            sage: I.gens()
            (e_1^2, e_1*f_1, f_1^2 - 2*e_1*h_1, f_1*h_1, h_1^2)
        """
        return self._gens

    def is_zero(self):
        """
        Whether this ideal is the zero ideal.

        EXAMPLES::

            sage: V = vertex_algebras.Virasoro(QQ, 1/2);
            sage: Q = V.quotient(V.ideal(V.find_singular(6)))
            sage: P = Q.arc_algebra(); I = P.defining_ideal()
            sage: I.is_zero()
            False
            sage: R = V.classical_limit(); J = R.ideal(0)
            sage: J.is_zero()
            True
            sage: R.quotient(J)
            The classical limit of The Virasoro vertex algebra of central charge 1/2 over Rational Field
        """
        return all(g.is_zero() for g in self.gens())

    def _ideal_gens(self, ord):
        """
        The generators of the ideal as an ideal in commutative rings.

        INPUT:

        - ``ord`` -- a positive rational number

        OUTPUT:

        The generators of this ideal, as an ideal of commutative rings,
        with conformal weight less than or equal to ``ord``.

        EXAMPLES::

            sage: V = vertex_algebras.Virasoro(QQ, 1/2);
            sage: P = V.classical_limit(); P.inject_variables()
            Defining L
            sage: I = P.ideal(L**3)
            sage: I._ideal_gens(9)
            (L_2^3,
             3*L_3*L_2^2,
             6*L_3^2*L_2 + 6*L_4*L_2^2,
             6*L_3^3 + 36*L_4*L_3*L_2 + 18*L_5*L_2^2)

            sage: V = vertex_algebras.Abelian(QQ, 4, weights = (1,1,1/2,1/2), parity=(0,0,1,1), names = ('a0','a1','b0','b1'))
            sage: P = V.classical_limit(); P.inject_variables()
            Defining a0, a1, b0, b1
            sage: I = P.ideal(a0*b1 + a1*b0)
            sage: I._ideal_gens(7/2)
            (a1_1*b0_1/2 + a0_1*b1_1/2,
             a0_2*b1_1/2 + a1_2*b0_1/2 + a1_1*b0_3/2 + a0_1*b1_3/2,
             2*a1_2*b0_3/2 + 2*a0_2*b1_3/2 + 2*a0_3*b1_1/2 + 2*a1_3*b0_1/2 + 2*a1_1*b0_5/2 + 2*a0_1*b1_5/2)
        """
        if ord not in QQ or ord < 0:
            raise ValueError("ord must be a non-negative rational number")
        from sage.functions.other import floor
        return tuple(g.T(j) for g in self.gens()\
                     for j in range(floor(ord+1-g.weight())))

    def _groebner_basis(self, ord, termorder='wdegrevlex'):
        """
        Return a Groebner basis for this ideal as a ring ideal.

        INPUT:

        - ``ord`` -- a non-negative integer; stop at this degree
        - ``termorder`` -- one of ``'wdegrevlex'``, ``'wdeglex'``,
          ``'revlexwdeg'`` or ``'lexwdeg'``
          (default: ``'wdegrevlex'``); the monomial order to use

        .. NOTE::

            This method is only supported on polynomial differential
            algebras and their quotients.

        EXAMPLES::

            sage: V = vertex_algebras.Virasoro(QQ, 1/2);
            sage: Q = V.quotient(V.ideal(V.find_singular(6))); P = Q.arc_algebra()
            sage: I = P.defining_ideal()
            sage: I._groebner_basis(10)
            [L_3^2*L_4 + L_2*L_4^2 + 2*L_2*L_3*L_5 + L_2^2*L_6, L_3^3 + 6*L_2*L_3*L_4 + 3*L_2^2*L_5, L_2*L_3^2 + L_2^2*L_4, L_2^2*L_3, L_2^3]
            sage: V = vertex_algebras.Affine(QQ,'A1', 1, names = ('e','f','h'));
            sage: Q = V.quotient(V.ideal(V.find_singular(2))); P = Q.arc_algebra()
            sage: I = P.defining_ideal()
            sage: I._groebner_basis(4)
            [e_2^2 + 2*e_1*e_3, e_2*f_2 + f_1*e_3 + e_1*f_3, f_2^2 - 2*e_2*h_2 - 2*h_1*e_3 + 2*f_1*f_3 - 2*e_1*h_3, f_2*h_2 + h_1*f_3 + f_1*h_3, h_2^2 + 2*h_1*h_3, e_1*e_2, f_1*e_2 + e_1*f_2, h_1*e_2 - f_1*f_2 + e_1*h_2, h_1*f_2 + f_1*h_2, h_1*h_2, e_1^2, e_1*f_1, f_1^2 - 2*e_1*h_1, f_1*h_1, h_1^2]
            sage: I._groebner_basis(4,'lexwdeg')
            [e_3*e_1 + 1/2*e_2^2, e_3*f_1 + e_2*f_2 + e_1*f_3, e_3*h_1 + e_2*h_2 + e_1*h_3 - f_3*f_1 - 1/2*f_2^2, f_3*h_1 + f_2*h_2 + f_1*h_3, f_2*f_1^2, f_1^2*h_2, h_3*h_1 + 1/2*h_2^2, e_2*e_1, e_2*f_1 + e_1*f_2, e_2*h_1 + e_1*h_2 - f_2*f_1, f_2*h_1 + f_1*h_2, f_1^3, h_2*h_1, e_1^2, e_1*f_1, e_1*h_1 - 1/2*f_1^2, f_1*h_1, h_1^2]
        """
        try:
            P = self._ambient.jet_algebra(ord, termorder)
        except NotImplementedError:
            raise NotImplementedError("_groebner_basis is not implemented for "\
                                 "ideals of {}".format(self._ambient))

        I = P.ideal([P(m._to_polynomial(ord)) for m in self._ideal_gens(ord)])
        return I.groebner_basis(deg_bound=ord)

    def hilbert_series(self,ord):
        """
        The graded dimension of the quotient by this ideal.

        INPUT:

        - ``ord`` -- a non-negative rational; the order of this series

        EXAMPLES::

            sage: V = vertex_algebras.NeveuSchwarz(QQ, 7/10)
            sage: Q = V.quotient(V.ideal(V.find_singular(4)))
            sage: P = Q.arc_algebra(); I = P.defining_ideal()
            sage: I.hilbert_series(11/2)
            1 + q^(3/2) + q^2 + q^(5/2) + q^3 + 2*q^(7/2) + 2*q^4 + 3*q^(9/2) + 2*q^5 + O(q^(11/2))
        """
        if self.is_zero():
            return self._ambient.hilbert_series(ord)
        try:
            P = self._ambient.jet_algebra(ord)
        except NotImplementedError:
            return self._ambient.quotient(self).hilbert_series(ord)
        GB = self._groebner_basis(ord)
        GBLM = [a.lm() for a in GB if a.degree() <= ord]
        J = P.ideal(GBLM)
        mydegreelist = [d.degree() for d in P.gens()]
        from sage.rings.power_series_ring import PowerSeriesRing
        q = PowerSeriesRing(ZZ,'q',default_prec=ord).gen()
        return J.hilbert_series(grading=mydegreelist)(q)

class PoissonVertexAlgebraIdealElement(IndexedFreeModuleElement):
    """
    Base class for elements on a classical limit of vertex algebras.
    """

    def _repr_(self):
        """
        String representation.

        EXAMPLES::

            sage: V = vertex_algebras.Affine(QQ,'A1', 1, names = ('e','f','h'));
            sage: P = V.classical_limit()
            sage: P.an_element()
            1 + 2*e_1 + 3*f_1 + e_1^4*f_2*f_1^2*h_3*h_1
        """
        return repr(self.lift())

    def lift(self):
        """
        Lift this element to the quantization of this Poisson vertex
        algebra.

        EXAMPLES::

            sage: V = vertex_algebras.NeveuSchwarz(QQ,1)
            sage: P = V.classical_limit()
            sage: v = P.an_element()
            sage: v
            1 + 2*G_3/2 + 3*L_2 + L_2*G_3/2
            sage: v.lift()
            |0> + 2*G_-3/2|0> + 3*L_-2|0> + L_-2G_-3/2|0>
        """
        return self.parent().lift(self)


class PoissonVertexAlgebraIdealBasis(Parent):
    def __init__(self,V,gens):
        """
        A basis for a vertex algebra ideal.

        This class implements the necessary methods to construct an
        infinite dimensional submodule of a vertex algebra (which itself
        is an infinite dimensional module) as well as to construct the
        corresponding quotient.

        INPUT:

        - ``V`` -- a :class:`PoissonVertexAlgebra`; the ambient of the
          ideal
        - ``gens`` -- a list or tuple of elements in ``V``; the
          generators of the ideal

        EXAMPLES::

            sage: V = vertex_algebras.Virasoro(QQ)
            sage: P = V.classical_limit()
            sage: P.inject_variables()
            Defining L
            sage: I = P.ideal(L**3)
            sage: I._indices
            Basis of the Poisson vertex algebra ideal of The classical limit of The Virasoro vertex algebra of central charge 0 over Rational Field generated by (L_2^3,)
        """
        self._ambient = V
        self._gens = gens
        Parent.__init__(self, category=InfiniteEnumeratedSets())

    def _repr_(self):
        """
        The name of this class.

        EXAMPLES::

            sage: V = vertex_algebras.Abelian(QQ, 6, weights = (1,1,1,1/2,1/2,1/2), parity=(0,0,0,1,1,1), names = ('a0','a1','a2','b0','b1','b2'))
            sage: P = V.classical_limit()
            sage: P.inject_variables()
            Defining a0, a1, a2, b0, b1, b2
            sage: I = P.ideal(a0**3*b1 - a1*a2**2*b2)
            sage: I._indices
            Basis of the Poisson vertex algebra ideal of The classical limit of The Abelian vertex algebra over Rational Field with generators (a0_-1|0>, a1_-1|0>, a2_-1|0>, b0_-1/2|0>, b1_-1/2|0>, b2_-1/2|0>) generated by (a0_1^3*b1_1/2 - a1_1*a2_1^2*b2_1/2,)
        """
        return "Basis of the Poisson vertex algebra ideal of {} generated by "\
               "{}".format(self._ambient,self._gens)

    def _element_constructor_(self,x):
        """
        Construct an element in this basis.

        INPUT:

        - ``x`` -- a pair ``(k,v)`` where ``k`` is a non-negative
          rational number (the degree of this vector) and ``v`` is
          either a basis index of the space of conformal weight ``k``
          as returned by :meth:`get_weight` or a basis element.

        EXAMPLES::

            sage: V = vertex_algebras.Abelian(QQ, 6, weights = (1,1,1,1/2,1/2,1/2), parity=(0,0,0,1,1,1), names = ('a0','a1','a2','b0','b1','b2'))
            sage: P = V.classical_limit()
            sage: P.inject_variables()
            Defining a0, a1, a2, b0, b1, b2
            sage: I = P.ideal(a0**3*b1 - a1*a2**2*b2); B = I._indices
            sage: B([4,0])
            (4, B[0])
            sage: M = I.get_weight(4)
            sage: R = M.basis()
            sage: B([4,R[0]])
            (4, B[0])
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

            sage: V = vertex_algebras.Abelian(QQ, 6, weights = (1,1,1,1/2,1/2,1/2), parity=(0,0,0,1,1,1), names = ('a0','a1','a2','b0','b1','b2'))
            sage: P = V.classical_limit()
            sage: P.inject_variables()
            Defining a0, a1, a2, b0, b1, b2
            sage: I = P.ideal(a0**3*b1 - a1*a2**2*b2)
            sage: I._indices[0:10]
            [(7/2, B[0]),
             (4, B[0]),
             (4, B[1]),
             (4, B[2]),
             (9/2, B[0]),
             (9/2, B[1]),
             (9/2, B[2]),
             (9/2, B[3]),
             (9/2, B[4]),
             (9/2, B[5])]
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

        The subspace of the ambient Poisson vertex algebra generated by
        all vectors of energy ``n`` in this basis.

        EXAMPLES::

            sage: V = vertex_algebras.Abelian(QQ, 6, weights = (1,1,1,1/2,1/2,1/2), parity=(0,0,0,1,1,1), names = ('a0','a1','a2','b0','b1','b2'))
            sage: P = V.classical_limit()
            sage: P.inject_variables()
            Defining a0, a1, a2, b0, b1, b2
            sage: I = P.ideal(a0**3*b1 - a1*a2**2*b2)
            sage: I._indices.get_weight(9/2)
            Free module generated by {0, 1, 2, 3, 4, 5} over Rational Field
        """
        p = self._ambient
        basis = [p(pt)*g.T(m) for g in self._gens for m in range(floor(n -
                 g.weight())+1)  for pt in p.indices().subset(
                 energy=n-g.weight()-m) ]

        return self._ambient.submodule(basis)

    def __getitem__(self,r):
        """
        List elements in this basis.

        EXAMPLES::

            sage: V = vertex_algebras.Abelian(QQ, 6, weights = (1,1,1,1/2,1/2,1/2), parity=(0,0,0,1,1,1), names = ('a0','a1','a2','b0','b1','b2'))
            sage: P = V.classical_limit()
            sage: P.inject_variables()
            Defining a0, a1, a2, b0, b1, b2
            sage: I = P.ideal(a0**3*b1 - a1*a2**2*b2)
            sage: I._indices[4]
            (9/2, B[0])
            sage: I._indices[2:6]
            [(4, B[1]), (4, B[2]), (9/2, B[0]), (9/2, B[1])]
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
