r"""
T-Systems and Q-Systems

AUTHORS:

- Travis Scrimshaw (2013-10-08): Initial version
"""

#*****************************************************************************
#  Copyright (C) 2013 Travis Scrimshaw <tscrim at ucdavis.edu>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
#*****************************************************************************

from sage.misc.lazy_attribute import lazy_attribute
from sage.misc.cachefunc import cached_method
from sage.misc.misc_c import prod
from sage.misc.bindable_class import BindableClass
from sage.structure.parent import Parent
from sage.structure.unique_representation import UniqueRepresentation

from sage.categories.hopf_algebras import HopfAlgebras
from sage.categories.realizations import Realizations, Category_realization_of_parent
from sage.rings.all import ZZ, QQ
from sage.rings.infinity import infinity
from sage.rings.arith import LCM
from sage.rings.polynomial.polynomial_ring_constructor import PolynomialRing
from sage.sets.family import Family
from sage.sets.positive_integers import PositiveIntegers
from sage.sets.disjoint_union_enumerated_sets import DisjointUnionEnumeratedSets
from sage.combinat.cartesian_product import CartesianProduct
from sage.combinat.free_module import CombinatorialFreeModule
from sage.monoids.indexed_free_monoid import IndexedFreeAbelianMonoid, IndexedMonoid
from sage.matrix.constructor import matrix
from sage.combinat.root_system.cartan_type import CartanType
from sage.combinat.root_system.cartan_matrix import CartanMatrix

class IntegrableSystem(CombinatorialFreeModule):
    """
    An integrable system.
    """
    def __init__(self, base_ring, cartan_type, level, gen_indices, name="I", category=None):
        r"""
        Initialize ``self``.

        EXAMPLES::

            sage: T = TSystem(QQ, ['A',4])
            sage: TestSuite(T).run()
        """
        if category is None:
            category = HopfAlgebras(base_ring).Commutative()
        self._cartan_type = cartan_type
        self._name = name
        self._level = level
        bases = IndexedFreeAbelianMonoid(gen_indices, prefix=name, bracket=False)
        CombinatorialFreeModule.__init__(self, base_ring, bases,
                                         prefix=name, category=category)

    def _repr_(self):
        r"""
        Return a string representation of ``self``.

        EXAMPLES::

            sage: TSystem(QQ, ['A',4])
            The T-system of type ['A', 4] over Rational Field
        """
        if self._level is not None:
            res = "restricted level {} ".format(self._level)
        else:
            res = ''
        return "{}{}-system of type {} over {}".format(res, self._name, self._cartan_type, self.base_ring())

    def level(self):
        """
        Return the restriction level of ``self`` or ``None`` if the system
        is unrestricted.
        """
        return self._level

    def cartan_type(self):
        """
        Return the Cartan type of ``self``.
        """
        return self._cartan_type

    def index_set(self):
        """
        Return the index set of ``self``.
        """
        return self._cartan_type.index_set()

    @cached_method
    def one(self):
        """
        Return the element `1`.

        EXAMPLES::

            sage: T = TSystem(QQ, ['A',4])
            sage: T.one()
            ()
        """
        return self.element_class(self, {self._indices.one(): self.base_ring().one()})

    def ngens(self):
        """
        Return the number of generators of ``self``.

        EXAMPLES::

            sage: Y = Yangian(QQ, 4)
            sage: Y.ngens()
            +Infinty
        """
        return infinity

    def dimension(self):
        """
        Return the dimension of ``self``, which is `\infty`.

        EXAMPLES::

            sage: Y = Yangian(QQ, 4)
            sage: Y.dimension()
            +Infinity
        """
        return infinity

    @lazy_attribute
    def _diagonal(self):
        """
        Return the diagonal of the symmetrized Cartan matrix of ``self``.
        """
        d = self._cartan_type.cartan_matrix().is_symmetrizable(True)
        lcd = LCM([QQ(x).denominator() for x in d])
        return Family({a: ZZ(d[i]*lcd) for i,a in enumerate(self.index_set())})

    @lazy_attribute
    def _lcm_diagonal(self):
        """
        Return the least common multiple of the diagonal.
        """
        return LCM(list(self._diagonal))

###################
## T-system

class TSystem(IntegrableSystem):
    r"""
    A T-system.

    We follow Equation (4.31-4.33) in [T-system, Y-Systems...].

    INPUT:

    - ``base_ring`` -- the base ring
    - ``cartan_type`` -- the Cartan type
    - ``spectral_ring`` -- the ring containing the spectral parameters
    - ``level`` -- (optional) the restriction level

    EXAMPLES::

        sage: R.<u> = QQ[]
        sage: T = TSystem(R, ['A',4])
    """
    @staticmethod
    def __classcall__(cls, base_ring, cartan_type, spectral_ring=None, level=None):
        """
        Normalize arguments to ensure a unique representation.
        """
        if spectral_ring is None:
            spectral_ring = base_ring
        cartan_type = CartanType(cartan_type)
        return super(TSystem, cls).__classcall__(cls, base_ring, cartan_type, spectral_ring, level)

    def __init__(self, base_ring, cartan_type, spectral_ring, level):
        r"""
        Initialize ``self``.

        EXAMPLES::

            sage: T = TSystem(QQ, ['A',4])
            sage: TestSuite(T).run()
        """
        category = HopfAlgebras(base_ring).Commutative().WithBasis()
        # This isn't quite right since we just have m = 1, but we need all
        #   positive integers in order to use it in the reduction steps.
        indices = CartesianProduct(cartan_type.index_set(), PositiveIntegers(), spectral_ring)
        IntegrableSystem.__init__(self, base_ring, cartan_type, level, indices, 'T', category)

    def _repr_term(self, t):
        """
        Return a string representation of the basis element indexed by ``m``.

        EXAMPLES::

            sage: T = TSystem(QQ, ['A',4])
            sage: T._repr_term(((3,1,2), (4,3,1)))
            'T^(3)[1](2)*T(4)[3](1)'
        """
        if len(t) == 0:
            return '1'
        def repr_gen(x):
            ret = 'T^({})[{}]({})'.format(*(x[0]))
            if x[1] > 1:
                ret += '^{}'.format(x[1])
            return ret
        return '*'.join(repr_gen(x) for x in t._sorted_items())

    def _latex_term(self, t):
        r"""
        Return a `\LaTeX` representation of the basis element indexed
        by ``m``.

        EXAMPLES::

            sage: T = TSystem(QQ, ['A',4])
            sage: T._latex_term(((3,1,2), (4,3,1)))
            'T^{(3)}_{1}(2) T^{(4)}_{3}(1)'
        """
        if len(t) == 0:
            return '1'
        def repr_gen(x):
            ret = 'T^{{({})}}_{{{}}}({})'.format(*(x[0]))
            if x[1] > 1:
                ret = '\\bigl(' + ret + '\\bigr)^{{{}}}'.format(x[1])
            return ret
        return ' '.join(repr_gen(x) for x in t._sorted_items())

    def gen(self, a, m, u):
        """
        Return the generator `T^{(a)}_i(u)` of ``self``.

        EXAMPLES::

            sage: T = TSystem(QQ, ['A',4])
            sage: T.gen(2, 1, 3)
            T^(2)[1](3)
            sage: T.gen(1, 2, 1)
            T^(12)[2](1)

        We can also use an indeterminant in the base ring::

            sage: R.<u> = QQ[]
            sage: T = TSystem(R, ['A',4])
            sage: T.gen(2, 1, u)
            T^(2)[1](3)
            sage: T.gen(4, 2, u)
            T^(12)[2](1)

        We check some variables that are formally defined, but are not
        honest T-system generators::

            sage: T.gen(0, 1, u)
            0
            sage: T.gen(1, 0, u)
            1
            sage: T.gen(1, -5, u)
            0
        """
        if m == 0 or m == self._level or a == 0 or a == len(self.index_set()) + 1:
            return self.one()
        if m == 1:
            return self.monomial(self._indices.gen((a,m,u)))
        if a not in self.index_set() or m < 0:
            return self.zero()
        if self._cartan_type.type() == 'A' and self._level is None:
            return self._jacobi_trudy(a, m, u)
        return self._reduced_generator(a, m, u)

    # TODO: Compute the determinant for general u and store that, then
    #   specialize to the spectral parameter
    @cached_method
    def _jacobi_trudy(self, a, m, u):
        """
        If we are in type `A_r` and an unrestricted T-system, use the
        Jacobi-Trudy type identity to reduce the generator `T^{(a)}_m(u)`
        into terms of `T^{(b)}_1(v)`.

        EXAMPLES::

            sage: R.<u> = QQ[]
            sage: T = TSystem(R, ['A',2])
            sage: T._jacobi_trudy(1, 3, u)
            1 + T^(1)[1](u - 2)*T^(1)[1](u)*T^(1)[1](u + 2)
             - T^(1)[1](u + 2)*T^(2)[1](u - 1) - T^(1)[1](u - 2)*T^(2)[1](u + 1)
            sage: all(T._jacobi_trudy(a,m,u) == T._reduced_generator(a,m,u)
            ....:     for a in T.index_set() for m in range(6))
            True
        """
        mat = []
        r = self._cartan_type.rank()
        for i in range(1,m+1):
            mat.append([])
            for j in range(1,m+1):
                b = a - i + j
                if b < 0 or b > r + 1:
                    mat[-1].append(self.zero())
                elif b == 0 or b == r + 1:
                    mat[-1].append(self.one())
                else:
                    mat[-1].append(self.gen(b, 1, u + i + j - m - 1))
        from sage.matrix.constructor import matrix
        return matrix(self, mat).determinant('pari')

    @cached_method
    def _reduced_generator(self, a, m, u):
        """
        Return the reduction of the generator `T^{(a)}_m(u)` into
        the variables `T^{(b)}_1(v)`.

        EXAMPLES::

            sage: R.<u> = QQ[]
            sage: T = TSystem(R, ['A',2])
            sage: T._reduced_generator(1,3,u)
            1 + T^(1)[1](u - 2)*T^(1)[1](u)*T^(1)[1](u + 2)
             - T^(1)[1](u + 2)*T^(2)[1](u - 1) - T^(1)[1](u - 2)*T^(2)[1](u + 1)
        """
        if m == 0 or m == self._level:
            return self.one()
        I = self._indices
        if m == 1:
            return self.monomial(I.gen((a,m,u)))

        # Do the first level
        plus,minus = self._reduce_gen_one_step(a, m, u)
        expand = lambda p,m: self.monomial(I.prod(I.gen(x) for x in p)) \
                             - self.monomial(I.prod(I.gen(x) for x in m))
        if m == 2: # Nothing more todo since all m is 1 and we are dividing by 1
            return expand(plus, minus)

        # Do the second level and expand
        f = lambda x: self._reduce_gen_one_step(*x)
        plus = map(f, plus)
        minus = map(f, minus)
        cur = self.prod(expand(*x) for x in plus)
        cur -= self.prod(expand(*x) for x in minus)

        # Now that everything has cancelled termwise, do the division and the reduction
        return self.sum(v * self.prod(self.gen(*k)**p
                                      for k,p in t.cancel(I.gen((a, m-2,u)))._sorted_items() )
                        for t,v in cur)

    @cached_method
    def _reduce_gen_one_step(self, a, m, u):
        """
        Return the product term of the generator `T^{(a)}_m(u)` expanded in
        terms of `T^{(b)}_{m-1}(v)`.

        OUTPUT:

        A tuple of the indices of the generators.
        """
        if m == 1:
            return ()
        d = self._diagonal
        da = d[a]
        t = self._lcm_diagonal
        I = self._indices

        cur = [((a, m-1, u - d[a] / t), (a, m-1, u + d[a] / t))]
        if da > 1:
            cur.append(tuple((b, da * (m-1) // d[b], u)
                    for b in self._cartan_type.dynkin_diagram().neighbors(a)))
        else:
            cur.append(tuple((b, 1 + (m-1-k) // d[b],
                              u + (2*k-m + ((m-1-k) // d[b])*d[b]) / t)
                    for b in self._cartan_type.dynkin_diagram().neighbors(a)
                    for k in range(1, d[b]+1)))
        return tuple(cur)

    def alternate(self):
        """
        Return the alternate presentation of ``self``.
        """
        return TSystemAlternate(self.base_ring(), self._cartan_type, self._level)

    def restriction_on_basis(self, m):
        """
        Return the restriction of the basis element indexed by ``m``.

        The restriction is defined by forgetting about the special
        parameter `u`, thus the result is in the corresponding Q-system.
        """
        F = QSystem(self.base_ring(), self._cartan_type, self._level).Fundamental()
        I = F._indices
        return Q.prod(Q.gen(*g)**p for g,p in m._sorted_items()))

    class Element(CombinatorialFreeModule.Element):
        def restriction(self):
            """
            Return the restriction of ``self`` to the corresponding Q-system.

            The restriction is defined by forgetting about the special
            parameter `u`.
            """
            Q = QSystem(self.base_ring(), self._cartan_type, self._level)
            return Q(self)

        def _mul_(self, x):
            """
            Return the product of ``self`` and ``x``.
            """
            return self.parent().sum_of_terms((tl*tr, cl*cr)
                                              for tl,cl in self for tr,cr in x)

# TODO: Use multiple realizations and give this a better name
# The first one could be called the fundamental presentation since it is given
#   in terms of the fundamental representations
# Perhaps this one could be called the row presentation since it corresponds
#   to single row KR crystals
class TSystemAlternate(TSystem):
    r"""
    A T-system solved in variables `T^{(1)}_k(v)` instead of `T^{(b)}_m(v)`.

    INPUT:

    - ``base_ring`` -- the base ring
    - ``cartan_type`` -- the Cartan type

    EXAMPLES::

        sage: R.<u> = QQ[]
        sage: T = TSystem(R, ['A',4]).alternate()
    """
    def gen(self, a, m, u):
        """
        Return the generator `T^{(a)}_m(u)` of ``self``.

        EXAMPLES::
        """
        if m == 0 or m == self._level or a == 0 or a == len(self.index_set()) + 1:
            return self.one()
        if a == 1:
            return self.monomial(self._indices.gen((a,m,u)))
        if a not in self.index_set():
            return self.zero()
        if self._cartan_type.type() == 'A' and self._level is None:
            return self._jacobi_trudy(a, m, u)
        raise NotImplementedError("TODO: Implement the algorithm to reduce to T^(1)[k](v)")
        return self._reduced_generator(a, m, u)

    @cached_method
    def _jacobi_trudy(self, a, m, u):
        """
        If we are in type `A_r` and an unrestricted T-system, use the
        Jacobi-Trudy type identity to reduce the generator `T^{(a)}_m(u)`
        into terms of `T^{(1)}_k(v)`.

        EXAMPLES::

            sage: R.<u> = QQ[]
            sage: T = TSystem(R, ['A',2])
            sage: T._jacobi_trudy(1, 3, u)
            1 + T^(1)[1](u - 2)*T^(1)[1](u)*T^(1)[1](u + 2)
             - T^(1)[1](u + 2)*T^(2)[1](u - 1) - T^(1)[1](u - 2)*T^(2)[1](u + 1)
            sage: all(T._jacobi_trudy(a,m,u) == T._reduced_generator(a,m,u)
            ....:     for a in T.index_set() for m in range(6))
            True
        """
        mat = []
        r = self._cartan_type.rank()
        for i in range(1, a+1):
            mat.append([])
            for j in range(1, a+1):
                k = m - i + j
                if k < 0:
                    mat[-1].append(self.zero())
                elif k == 0:
                    mat[-1].append(self.one())
                else:
                    mat[-1].append(self.gen(1, k, u + i + j - a - 1))
        from sage.matrix.constructor import matrix
        return matrix(self, mat).determinant('pari')

    def alternate(self):
        """
        Return the alternate presentation of ``self``.
        """
        return TSystem(self.base_ring(), self._cartan_type, self._level)

###################
## Q-systems

class QSystem(Parent, UniqueRepresentation):
    r"""
    A Q-system.

    We use the presentation of a Q-system given in [HKOTY99]_.

    The relation is:

    .. MATH::

        (Q_m^{(a)})^2 = Q_{m+1}^{(a)} Q_{m-1}^{(a)} +
        \prod_{b \sim a} \prod_{k=0}^{-C_{ab} - 1}
        Q^{(b)}_{\lfloor \frac{m C_{ba} - k}{C_{ab}} \rfloor}

    with `Q^{(a)}_0 = 1`.

    Q-systems have two natural bases:

    - ``Fundamental`` -- given by polynomials of the
      fundamental representations
    - ``SqaureFree`` -- given by square-free terms

    REFERENCES:

    .. [HKOTY99] G. Hatayama, A. Kuniba, M. Okado, T. Tagaki, and Y. Yamada.
       *Remarks on the fermionic formula*. Contemp. Math., **248** (1999).
    """
    @staticmethod
    def __classcall__(cls, base_ring, cartan_type, level=None):
        """
        Normalize arguments to ensure a unique representation.
        """
        cartan_type = CartanType(cartan_type)
        # TODO: Check for tamely laced!!!
        return super(QSystem, cls).__classcall__(cls, base_ring, cartan_type, level)

    def __init__(self, base_ring, cartan_type, level):
        """
        Initialize ``self``.

        EXAMPLES::

            sage: Q = QSystem(QQ, ['A',4])
            sage: TestSuite(Q).run()
        """
        category = HopfAlgebras(base_ring).Commutative()
        self._cartan_type = cartan_type
        self._level = level
        Parent.__init__(self, base_ring, category=category.WithRealizations())

    def _repr_(self):
        r"""
        Return a string representation of ``self``.

        EXAMPLES::

            sage: QSystem(QQ, ['A',4])
            Q-system of type ['A', 4] over Rational Field
        """
        if self._level is not None:
            res = "Restricted level {} ".format(self._level)
        else:
            res = ''
        return "{}Q-system of type {} over {}".format(res, self._cartan_type, self.base_ring())

    def cartan_type(self):
        """
        Return the Cartan type of ``self``.
        """
        return self._cartan_type

    def level(self):
        """
        Return the restriction level of ``self`` or ``None`` if
        the system is unrestricted.
        """
        return self._level

    def a_realization(self):
        r"""
        Return a particular realization of ``self`` (the fundamental basis).

        EXAMPLES::
        """
        return self.Fundamental()

    class _BasesCategory(Category_realization_of_parent):
        r"""
        The category of bases of a Iwahori-Hecke algebra.
        """
        def super_categories(self):
            r"""
            The super categories of ``self``.

            EXAMPLES::

                sage: Q = QSystem(QQ, ['A',4])
                sage: bases = Q._BasesCategory()
                sage: bases.super_categories()
                [Category of realizations of Q-system of type ['A', 4] over Rational Field,
                 Category of commutative hopf algebras with basis over quotient fields]
            """
            cat = HopfAlgebras(self.base().base_ring().category()).Commutative().WithBasis()
            return [Realizations(self.base()), cat]

        def _repr_(self):
            r"""
            Return the representation of ``self``.

            EXAMPLES::

                sage: Q = QSystem(QQ, ['A',4])
                sage: Q._BasesCategory()
                Category of bases of Q-system of type ['A', 4] over Rational Field
            """
            return "Category of bases of {}".format(self.base())

        class ParentMethods:
            r"""
            This class collects code common to all the various bases.
            """
            def _repr_(self):
                """
                Text representation of this basis of Iwahori-Hecke algebra.

                EXAMPLES::

                    sage: Q = QSystem(QQ, ['A',4])
                    sage: Q.Fundamental()
                    Q-system of type ['A', 4] over Rational Field
                     in the Fundamental basis
                    sage: Q.SquareFree()
                    Q-system of type ['A', 4] over Rational Field
                     in the Square-Free basis
                """
                return "{} in the {} basis".format(self.realization_of(), self._basis_name)

            def level(self):
                """
                Return the restriction level of ``self`` or ``None`` if
                the system is unrestricted.
                """
                return self._level

            def cartan_type(self):
                """
                Return the Cartan type of ``self``.
                """
                return self._cartan_type

            def index_set(self):
                """
                Return the index set of ``self``.
                """
                return self._cartan_type.index_set()

            @cached_method
            def one_basis(self):
                """
                Return the basis element indexing `1`.

                EXAMPLES::

                    sage: F = QSystem(QQ, ['A',4]).Fundamental()
                    sage: F.one_basis()
                    1
                    sage: F.one_basis().parent() is F._indices
                    True
                """
                return self._indices.one()

            @cached_method
            def algebra_generators(self):
                """
                Return the algebra generators of ``self``.

                EXAMPLES::

                    sage: Q = QSystem(QQ, ['A',4])
                    sage: Q.algebra_generators()
                    Finite family {1: Q^(1)[1], 2: Q^(2)[1], 3: Q^(3)[1], 4: Q^(4)[1]}
                """
                return Family({a: self.gen(a, 1) for a in self.index_set()})

            def dimension(self):
                """
                Return the dimension of ``self``, which is `\infty`.

                EXAMPLES::

                    sage: Y = Yangian(QQ, 4)
                    sage: Y.dimension()
                    +Infinity
                """
                return infinity

    class _BasisAbstract(CombinatorialFreeModule, BindableClass):
        """
        Abstract base class for a basis of a Q-system.
        """
        def __init__(self, Q_system, indices):
            r"""
            Initialize ``self``.

            EXAMPLES::

                sage: T = TSystem(QQ, ['A',4])
                sage: TestSuite(T).run()
            """
            self._cartan_type = Q_system._cartan_type
            self._level = Q_system._level
            category = Q_system._BasesCategory()
            CombinatorialFreeModule.__init__(self, Q_system.base_ring(), indices,
                                             prefix='Q', category=category)

        def _repr_term(self, t):
            """
            Return a string representation of the basis element indexed by ``a``
            with all `m = 1`.

            EXAMPLES::

                sage: Q = QSystem(QQ, ['A',4])
                sage: Q._repr_term(((1,1), (4,1)))
                'Q^(1)[1]*Q^(4)[1]'
            """
            if len(t) == 0:
                return '1'
            def repr_gen(x):
                ret = 'Q^({})[{}]'.format(*(x[0]))
                if x[1] > 1:
                    ret += '^{}'.format(x[1])
                return ret
            return '*'.join(repr_gen(x) for x in t._sorted_items())

        def _latex_term(self, t):
            r"""
            Return a `\LaTeX` representation of the basis element indexed
            by ``m``.

            EXAMPLES::

                sage: Q = QSystem(QQ, ['A',4])
                sage: Q._latex_term(((3,1,2), (4,1,1)))
                'Q^{(3)}_{1} Q^{(4)}_{1}'
            """
            if len(t) == 0:
                return '1'
            def repr_gen(x):
                ret = 'Q^{{({})}}_{{{}}}'.format(*(x[0]))
                if x[1] > 1:
                    ret = '\\bigl(' + ret + '\\bigr)^{{{}}}'.format(x[1])
                return ret
            return ' '.join(repr_gen(x) for x in t._sorted_items())

        def _coerce_map_from_(self, M):
            """
            Return a morphism if there is a coercion map from ``M``
            into ``self``.
            """
            if isinstance(M, TSystem):
                if (M.cartan_type() == self.cartan_type()
                    and self.base_ring().has_coerce_map_from(M.base_ring())):
                    return M.module_morphism(M.restriction_on_basis, codomain=self)
            return super(QSystem._BasisAbstract, self)._coerce_map_from_(M)

    class Fundamental(_BasisAbstract):
        """
        The basis of a Q-system given by polynomials of the
        fundamental representations.
        """
        _basis_name = "Fundamental"

        def __init__(self, Q_system):
            r"""
            Initialize ``self``.

            EXAMPLES::

                sage: Q = QSystem(QQ, ['A',4])
                sage: TestSuite(Q).run()
            """
            cartan_type = Q_system._cartan_type
            indices = CartesianProduct(cartan_type.index_set(), [1])
            basis = IndexedFreeAbelianMonoid(indices, prefix='Q', bracket=False)
            # This is used to do the reductions
            self._poly = PolynomialRing(ZZ, ['q'+str(i) for i in cartan_type.index_set()])
            QSystem._BasisAbstract.__init__(self, Q_system, basis)

        def gen(self, a, m):
            """
            Return the generator `Q^{(a)}_i` of ``self``.

            EXAMPLES::

                sage: Q = QSystem(QQ, ['A',4])
                sage: Q.gen(2, 1)
                Q^(2)[1]
                sage: Q.gen(12, 2)
                Q^(12)[2]
                sage: Q.gen(0, 1)
                1
                sage: Q.gen(1, 0)
                1
            """
            if m == 0 or m == self._level:
                return self.one()
            if m == 1:
                return self.monomial( self._indices.gen((a,1)) )
            assert a in self.index_set()
            #if self._cartan_type.type() == 'A' and self._level is None:
            #    return self._jacobi_trudy(a, m)
            I = self._cartan_type.index_set()
            p = self._Q_poly(a, m)
            return p.subs({ g: self.gen(I[i], 1) for i,g in enumerate(self._poly.gens()) })

        @cached_method
        def _jacobi_trudy(self, a, m):
            """
            If we are in type `A_r` and an unrestricted Q-system, use the
            Jacobi-Trudy type identity to reduce the generator `Q^{(a)}_m`
            into terms of `Q^{(b)}_1`.

            EXAMPLES::

                sage: R.<u> = QQ[]
                sage: T = TSystem(R, ['A',2])
                sage: T._jacobi_trudy(1, 3, u)
                1 + T^(1)[1](u - 2)*T^(1)[1](u)*T^(1)[1](u + 2)
                 - T^(1)[1](u + 2)*T^(2)[1](u - 1) - T^(1)[1](u - 2)*T^(2)[1](u + 1)
                sage: all(T._jacobi_trudy(a,m,u) == T._reduced_generator(a,m,u)
                ....:     for a in T.index_set() for m in range(6))
                True
            """
            mat = []
            r = self._cartan_type.rank()
            for i in range(1, m+1):
                mat.append([])
                for j in range(1, m+1):
                    b = a - i + j
                    if b < 0 or b > r + 1:
                        mat[-1].append(self.zero())
                    elif b == 0 or b == r + 1:
                        mat[-1].append(self.one())
                    else:
                        mat[-1].append(self.gen(b, 1))
            return matrix(self, mat).determinant('pari')

        @cached_method
        def _Q_poly(self, a, m):
            r"""
            Return the element `Q^{(a)}_m` as a polynomial.

            We start with the relation

            .. MATH::

                Q^{(a)}_{m-1}^2 = Q^{(a)}_m Q^{(a)}_{m-2} + \mathcal{Q}_{a,m-1},

            which implies

            .. MATH::

                Q^{(a)}_m = \frac{Q^{(a)}_{m-1}^2 - \mathcal{Q}_{a,m-1}}{
                Q^{(a)}_{m-2}}.
            """
            if m == 0 or m == self._level:
                return self._poly.one()
            if m == 1:
                return self._poly.gen(self._cartan_type.index_set().index(a))

            cm = CartanMatrix(self._cartan_type)
            I = self._cartan_type.index_set()
            m -= 1 # So we don't have to do it everywhere

            cur = self._Q_poly(a, m)**2
            i = I.index(a)
            ret = self._poly.one()
            for b in self._cartan_type.dynkin_diagram().neighbors(a):
                j = I.index(b)
                for k in range(-cm[i,j]):
                    ret *= self._Q_poly(b, (m * cm[j,i] - k) // cm[i,j])
            cur -= ret
            if m > 1:
                cur //= self._Q_poly(a, m-1)
            return cur

        class Element(CombinatorialFreeModule.Element):
            def _mul_(self, x):
                """
                Return the product of ``self`` and ``x``.
                """
                return self.parent().sum_of_terms((tl*tr, cl*cr)
                                                  for tl,cl in self for tr,cr in x)

    class SquareFree(_BasisAbstract):
        """
        The Q-system basis given in square free monomials.
        """
        _basis_name = "Square-Free"

        def __init__(self, Q_system):
            r"""
            Initialize ``self``.

            EXAMPLES::

                sage: SF = QSystem(QQ, ['A',2]).SquareFree()
                sage: TestSuite(SF).run()
            """
            basis = SquareFreeMonomials(Q_system._cartan_type)
            QSystem._BasisAbstract.__init__(self, Q_system, basis)

        def gen(self, a, m):
            """
            Return the generator `Q^{(a)}_i` of ``self``.

            EXAMPLES::

                sage: SF = QSystem(QQ, ['A',4]).SquareFree()
                sage: SF.gen(2, 1)
                Q^(2)[1]
                sage: SF.gen(12, 2)
                Q^(12)[2]
                sage: SF.gen(0, 1)
                1
                sage: Q.gen(1, 0)
                1
            """
            if m == 0 or m == self._level:
                return self.one()
            assert a in self.index_set()
            return self.monomial(self._indices.gen((a,m)))

        @lazy_attribute
        def _diagonal(self):
            """
            Return the diagonal of the symmetrized Cartan matrix of ``self``.
            """
            d = self._cartan_type.cartan_matrix().is_symmetrizable(True)
            lcd = LCM([QQ(x).denominator() for x in d])
            return Family({a: ZZ(d[i]*lcd) for i,a in enumerate(self.index_set())})

        @lazy_attribute
        def _lcm_diagonal(self):
            """
            Return the least common multiple of the diagonal.
            """
            return LCM(list(self._diagonal))

        def _reduce_square_free(self, a, m):
            r"""
            Return the square reduced by the formula

            .. MATH::

                \left( Q^{(a)}_m \right)^2 = Q^{(a)}_{m-1} Q^{(a)}_{m+1}
                + \prod_{a \sim b} Q(b)

            where if `d_a > 1` then `Q(b) = Q_{\beta}^{(b)}` where
            `\beta = d_a \left\lfloor \frac{m-1}{d_b} \right\rfloor`, otherwise

            .. MATH::

                Q(b) = \prod_{k=1}^{d_b} Q^{(b)}_{\beta_k}

            where `\beta_k = 1 + \left\lfloor \frac{m-1-k}{d_b} \right\rfloor`.
            """
            d = self._diagonal
            da = d[a]
            I = self._indices

            cur = self.gen(a,m-1) * self.gen(a,m+1)
            N = self._cartan_type.dynkin_diagram().neighbors(a)
            if da > 1:
                cur += self.prod(self.gen(b, (da * m) // d[b])
                                 for b in N)
            else:
                cur += self.prod(self.gen(b, 1 + (m-k) // d[b])
                                 for b in N for k in range(1, d[b]+1))
            return cur

        class Element(CombinatorialFreeModule.Element):
            def _mul_(self, x):
                """
                Return the product of ``self`` and ``x``.
                """
                P = self.parent()
                cur = P.sum_of_terms((tl*tr, cl*cr) for tl,cl in self for tr,cr in x)
                is_square_free = False
                while not is_square_free:
                    is_square_free = True
                    for m,c in cur:
                        ret = []
                        for a,exp in m._sorted_items():
                            if exp > 1:
                                assert exp == 2, "larger than square"
                                ret.append(P._reduce_square_free(*a))
                                is_square_free = False
                            else:
                                ret.append(P.gen(*a))
                        if not is_square_free:
                            cur += c * P.prod(ret) - P._from_dict({m:c}, remove_zeros=False)
                            break
                return cur


###########################################################
## Helper classes

class SquareFreeMonomials(IndexedFreeAbelianMonoid):
    """
    Parent representing the set of square-free monomials.
    """
    @staticmethod
    def __classcall__(cls, ct):
        """
        Normalize input.

        EXAMPLES::

            sage: from sage.algebras.t_q_system import SquareFreeMonomials
            sage: S1 = SquareFreeMonomials(['A',3])
            sage: S2 = SquareFreeMonomials('A3')
            sage: S1 is S2
            True
        """
        return super(IndexedMonoid, cls).__classcall__(cls, CartanType(ct))

    def __init__(self, cartan_type):
        """
        Initialize ``self``.

        EXAMPLES::

            sage: from sage.algebras.t_q_system import QSystem_square_free
            sage: Qsf = QSystem_square_free(QQ, ['A',2])
            sage: TestSuite(Qsf._indices).run()
        """
        self._cartan_type = cartan_type
        indices = CartesianProduct(cartan_type.index_set(), PositiveIntegers())
        IndexedFreeAbelianMonoid.__init__(self, indices, prefix='Q')

    def _repr_(self):
        """
        Return a string representation of ``self``.

        EXAMPLES::

            sage: from sage.algebras.t_q_system import QSystem_square_free
            sage: Qsf = QSystem_square_free(QQ, ['A',2])
            sage: Qsf._indices
            Square-free monomials of the Q-system of type ['A', 2]
        """
        return "Square-free monomials of the Q-system of type {}".format(self._cartan_type)

class TSystem_reducible(object):
    r"""
    The T-system that is used to perform the reduction steps.
    """
    def __init__(self, base_ring, cartan_type, level):
        r"""
        Initialize ``self``.

        EXAMPLES::

            sage: Q = QSystem(QQ, ['A',4])
            sage: TestSuite(Q).run()
        """
        self._cartan_type = cartan_type
        self._level = level
        self._poly = PolynomialRing(ZZ, ['q'+str(i) for i in cartan_type.index_set()])
        self._spec = PoylnomialRing(QQ, 'u')

    @lazy_attribute
    def _diagonal(self):
        """
        Return the diagonal of the symmetrized Cartan matrix of ``self``.
        """
        d = self._cartan_type.cartan_matrix().is_symmetrizable(True)
        lcd = LCM([QQ(x).denominator() for x in d])
        return Family({a: ZZ(d[i]*lcd) for i,a in enumerate(self.index_set())})

    @lazy_attribute
    def _lcm_diagonal(self):
        """
        Return the least common multiple of the diagonal.
        """
        return LCM(list(self._diagonal))

    @cached_method
    def _T_poly(self, a, m):
        r"""
        Return the element `T^{(a)}_m(u)` as a polynomial.

        We start with the relation

        .. MATH::

            Q^{(a)}_{m-1}^2 = Q^{(a)}_m Q^{(a)}_{m-2} + \mathcal{Q}_{a,m-1},

        which implies

        .. MATH::

            Q^{(a)}_m = \frac{Q^{(a)}_{m-1}^2 - \mathcal{Q}_{a,m-1}}{
            Q^{(a)}_{m-2}}.
        """
        if m == 0 or m == self._level:
            return self._poly.one()
        if m == 1:
            return self._poly.gen(self._cartan_type.index_set().index(a))

        cm = CartanMatrix(self._cartan_type)
        I = self._cartan_type.index_set()
        m -= 1 # So we don't have to do it everywhere

        cur = self._Q_poly(a, m)**2
        i = I.index(a)
        ret = self._poly.one()
        for b in self._cartan_type.dynkin_diagram().neighbors(a):
            j = I.index(b)
            for k in range(-cm[i,j]):
                ret *= self._Q_poly(b, floor((m * cm[j,i] - k) / cm[i,j]))
        cur -= ret
        if m > 1:
            cur //= self._Q_poly(a, m-1)
        return cur

