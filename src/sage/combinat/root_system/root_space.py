"""
Root lattices and root spaces
"""
#*****************************************************************************
#       Copyright (C) 2008-2009 Nicolas M. Thiery <nthiery at users.sf.net>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
#*****************************************************************************

from sage.misc.cachefunc import ClearCacheOnPickle, cached_method, cached_in_parent_method
from sage.rings.all import ZZ
from sage.combinat.free_module import CombinatorialFreeModule, CombinatorialFreeModuleElement
from root_lattice_realizations import RootLatticeRealizations
from sage.misc.cachefunc import cached_in_parent_method

# TODO: inheriting from ClearCacheOnPickle is a technical detail unrelated to root spaces
# could we abstract this somewhere higher?

class RootSpace(ClearCacheOnPickle, CombinatorialFreeModule):
    r"""
    The root space of a root system over a given base ring

    INPUT:

    - ``root_system`` - a root system
    - ``base_ring``: a ring `R`

    The *root space* (or lattice if ``base_ring`` is `\ZZ`) of a root
    system is the formal free module `\bigoplus_i R \alpha_i`
    generated by the simple roots `(\alpha_i)_{i\in I}` of the root system.

    This class is also used for coroot spaces (or lattices).

    .. seealso::

        - :meth:`RootSystem`
        - :meth:`RootSystem.root_lattice` and :meth:`RootSystem.root_space`
        - :meth:`~sage.combinat.root_system.root_lattice_realizations.RootLatticeRealizations`

    Todo: standardize the variable used for the root space in the examples (P?)

    TESTS::

        sage: for ct in CartanType.samples(crystallographic=True)+[CartanType(["A",2],["C",5,1])]:
        ...       TestSuite(ct.root_system().root_lattice()).run()
        ...       TestSuite(ct.root_system().root_space()).run()
        sage: r = RootSystem(['A',4]).root_lattice()
        sage: r.simple_root(1)
        alpha[1]
        sage: latex(r.simple_root(1))
        \alpha_{1}

    """

    def __init__(self, root_system, base_ring):
        """
        EXAMPLES::

            sage: P = RootSystem(['A',4]).root_space()
            sage: s = P.simple_reflections()

        """
        from sage.categories.morphism import SetMorphism
        from sage.categories.homset import Hom
        from sage.categories.sets_with_partial_maps import SetsWithPartialMaps
        self.root_system = root_system
        CombinatorialFreeModule.__init__(self, base_ring,
                                         root_system.index_set(),
                                         prefix = "alphacheck" if root_system.dual_side else "alpha",
                                         latex_prefix = "\\alpha^\\vee" if root_system.dual_side else "\\alpha",
                                         category = RootLatticeRealizations(base_ring))
        if base_ring is not ZZ:
            # Register the partial conversion back from ``self`` to the root lattice
            # See :meth:`_to_root_lattice` for tests
            root_lattice = self.root_system.root_lattice()
            SetMorphism(Hom(self, root_lattice, SetsWithPartialMaps()),
                        self._to_root_lattice
                        ).register_as_conversion()

    def _repr_(self):
        """
        EXAMPLES::

            sage: RootSystem(['A',4]).root_lattice()    # indirect doctest
            Root lattice of the Root system of type ['A', 4]
            sage: RootSystem(['B',4]).root_space()
            Root space over the Rational Field of the Root system of type ['B', 4]
            sage: RootSystem(['A',4]).coroot_lattice()
            Coroot lattice of the Root system of type ['A', 4]
            sage: RootSystem(['B',4]).coroot_space()
            Coroot space over the Rational Field of the Root system of type ['B', 4]

        """
        return self._name_string()

    def _name_string(self, capitalize=True, base_ring=True, type=True):
        """
        EXAMPLES::

            sage: RootSystem(['A',4]).root_space()._name_string()
            "Root space over the Rational Field of the Root system of type ['A', 4]"
        """
        return self._name_string_helper("root", capitalize=capitalize, base_ring=base_ring, type=type)

    simple_root = CombinatorialFreeModule.monomial

    @cached_method
    def to_coroot_space_morphism(self):
        """
        Returns the ``nu`` map to the coroot space over the same base ring, using the symmetrizer of the Cartan matrix

        It does not map the root lattice to the coroot lattice, but
        has the property that any root is mapped to some scalar
        multiple of its associated coroot.

        EXAMPLES::

            sage: R = RootSystem(['A',3]).root_space()
            sage: alpha = R.simple_roots()
            sage: f = R.to_coroot_space_morphism()
            sage: f(alpha[1])
            alphacheck[1]
            sage: f(alpha[1]+alpha[2])
            alphacheck[1] + alphacheck[2]

            sage: R = RootSystem(['A',3]).root_lattice()
            sage: alpha = R.simple_roots()
            sage: f = R.to_coroot_space_morphism()
            sage: f(alpha[1])
            alphacheck[1]
            sage: f(alpha[1]+alpha[2])
            alphacheck[1] + alphacheck[2]

            sage: S = RootSystem(['G',2]).root_space()
            sage: alpha = S.simple_roots()
            sage: f = S.to_coroot_space_morphism()
            sage: f(alpha[1])
            alphacheck[1]
            sage: f(alpha[1]+alpha[2])
            alphacheck[1] + 3*alphacheck[2]
        """
        R = self.base_ring()
        C = self.cartan_type().symmetrizer().map(R)
        return self.module_morphism(diagonal = C.__getitem__,
                                    codomain=self.coroot_space(R))

    def _to_root_lattice(self, x):
        """
        Try to convert ``x`` to the root lattice.

        INPUT:

        - ``x`` -- an element of ``self``

        EXAMPLES::

            sage: R = RootSystem(['A',3])
            sage: root_space = R.root_space()
            sage: x = root_space.an_element(); x
            2*alpha[1] + 2*alpha[2] + 3*alpha[3]
            sage: root_space._to_root_lattice(x)
            2*alpha[1] + 2*alpha[2] + 3*alpha[3]
            sage: root_space._to_root_lattice(x).parent()
            Root lattice of the Root system of type ['A', 3]

        This will fail if ``x`` does not have integral coefficients::

            sage: root_space._to_root_lattice(x/2)
            Traceback (most recent call last):
            ...
            ValueError: alpha[1] + alpha[2] + 3/2*alpha[3] does not have integral coefficients

        .. note::

            For internal use only; instead use a conversion::

                sage: R.root_lattice()(x)
                2*alpha[1] + 2*alpha[2] + 3*alpha[3]
                sage: R.root_lattice()(x/2)
                Traceback (most recent call last):
                ...
                ValueError: alpha[1] + alpha[2] + 3/2*alpha[3] does not have integral coefficients

        .. todo:: generalize diagonal module morphisms to implement this
        """
        try:
            return self.root_system.root_lattice().sum_of_terms( (i, ZZ(c)) for (i,c) in x)
        except TypeError:
            raise ValueError, "%s does not have integral coefficients"%x

    @cached_method
    def _to_classical_on_basis(self, i):
        r"""
        Implement the projection onto the corresponding classical root space or lattice, on the basis.

        EXAMPLES::

            sage: L = RootSystem(["A",3,1]).root_space()
            sage: L._to_classical_on_basis(0)
            -alpha[1] - alpha[2] - alpha[3]
            sage: L._to_classical_on_basis(1)
            alpha[1]
            sage: L._to_classical_on_basis(2)
            alpha[2]
        """
        if i == self.cartan_type().special_node():
            return self._classical_alpha_0()
        else:
            return self.classical().simple_root(i)

class RootSpaceElement(CombinatorialFreeModuleElement):
    def scalar(self, lambdacheck):
        """
        The scalar product between the root lattice and
        the coroot lattice.

        EXAMPLES::

            sage: L = RootSystem(['B',4]).root_lattice()
            sage: alpha      = L.simple_roots()
            sage: alphacheck = L.simple_coroots()
            sage: alpha[1].scalar(alphacheck[1])
            2
            sage: alpha[1].scalar(alphacheck[2])
            -1

        The scalar products between the roots and coroots are given by
        the Cartan matrix::

            sage: matrix([ [ alpha[i].scalar(alphacheck[j])
            ...              for i in L.index_set() ]
            ...            for j in L.index_set() ])
            [ 2 -1  0  0]
            [-1  2 -1  0]
            [ 0 -1  2 -1]
            [ 0  0 -2  2]

            sage: L.cartan_type().cartan_matrix()
            [ 2 -1  0  0]
            [-1  2 -1  0]
            [ 0 -1  2 -1]
            [ 0  0 -2  2]
        """
        # Find some better test
        #if not (lambdacheck in self.parent().coroot_lattice() or lambdacheck in self.parent().coroot_space()):
        #    raise TypeError, "%s is not in a coroot lattice/space"%(lambdacheck)
        zero = self.parent().base_ring().zero()
        cartan_matrix = self.parent().dynkin_diagram()
        return sum( (sum( (lambdacheck[i]*s for i,s in cartan_matrix.column(j)), zero) * c for j,c in self), zero)

    def is_positive_root(self):
        """
        Checks whether an element in the root space lies in the
        nonnegative cone spanned by the simple roots.

        EXAMPLES::

            sage: R=RootSystem(['A',3,1]).root_space()
            sage: B=R.basis()
            sage: w=B[0]+B[3]
            sage: w.is_positive_root()
            True
            sage: w=B[1]-B[2]
            sage: w.is_positive_root()
            False
        """
        return all( c.is_real_positive() for c in self.coefficients() ) # TODO: make it so that it is generic wrt the base_ring

    @cached_in_parent_method
    def associated_coroot(self):
        r"""
        Returns the coroot associated to this root

        OUTPUT:

        An element of the coroot space over the same base ring; in
        particular the result is in the coroot lattice whenever
        ``self`` is in the root lattice.

        EXAMPLES::

            sage: L = RootSystem(["B", 3]).root_space()
            sage: alpha = L.simple_roots()
            sage: alpha[1].associated_coroot()
            alphacheck[1]
            sage: alpha[1].associated_coroot().parent()
            Coroot space over the Rational Field of the Root system of type ['B', 3]

            sage: L.highest_root()
            alpha[1] + 2*alpha[2] + 2*alpha[3]
            sage: L.highest_root().associated_coroot()
            alphacheck[1] + 2*alphacheck[2] + alphacheck[3]

            sage: alpha = RootSystem(["B", 3]).root_lattice().simple_roots()
            sage: alpha[1].associated_coroot()
            alphacheck[1]
            sage: alpha[1].associated_coroot().parent()
            Coroot lattice of the Root system of type ['B', 3]

        """
        #assert(self in self.parent().roots() is not False)
        scaled_coroot = self.parent().to_coroot_space_morphism()(self)
        s = self.scalar(scaled_coroot)
        return scaled_coroot.map_coefficients(lambda c: (2*c) // s)

    def quantum_root(self):
        r"""
        Returns True if ``self`` is a quantum root and False otherwise.

        INPUT:

        - ``self`` -- an element of the nonnegative integer span of simple roots.

        A root `\alpha` is a quantum root if `\ell(s_\alpha) = \langle 2 \rho, \alpha^\vee \rangle - 1` where `\ell` is the length function, `s_\alpha` is the reflection across the hyperplane orthogonal to `\alpha`, and `2\rho` is the sum of positive roots.

        .. warning::

            This implementation only handles finite Cartan types and assumes that ``self`` is a root.

        .. TODO:: Rename to is_quantum_root

        EXAMPLES::

            sage: Q = RootSystem(['C',2]).root_lattice()
            sage: positive_roots = Q.positive_roots()
            sage: for x in positive_roots:
            ....:     print x, x.quantum_root()
            alpha[1] True
            alpha[2] True
            2*alpha[1] + alpha[2] True
            alpha[1] + alpha[2] False
        """

        return len(self.associated_reflection()) == -1 + (self.parent().positive_roots_nonparabolic_sum(())).scalar(self.associated_coroot())

    def max_coroot_le(self):
        r"""
        Returns the highest positive coroot whose associated root is less than or equal to ``self``.

        INPUT:

        - ``self`` -- an element of the nonnegative integer span of simple roots.

        Returns None for the zero element.

        Really ``self`` is an element of a coroot lattice and this method returns the highest root whose
        associated coroot is <= ``self``.

        .. warning::

            This implementation only handles finite Cartan types

        EXAMPLES::

            sage: root_lattice = RootSystem(['C',2]).root_lattice()
            sage: root_lattice.from_vector(vector([1,1])).max_coroot_le()
            alphacheck[1] + 2*alphacheck[2]
            sage: root_lattice.from_vector(vector([2,1])).max_coroot_le()
            alphacheck[1] + 2*alphacheck[2]
            sage: root_lattice = RootSystem(['B',2]).root_lattice()
            sage: root_lattice.from_vector(vector([1,1])).max_coroot_le()
            2*alphacheck[1] + alphacheck[2]
            sage: root_lattice.from_vector(vector([1,2])).max_coroot_le()
            2*alphacheck[1] + alphacheck[2]

            sage: root_lattice.zero().max_coroot_le() is None
            True
            sage: root_lattice.from_vector(vector([-1,0])).max_coroot_le()
            Traceback (most recent call last):
            ...
            ValueError: -alpha[1] is not in the positive cone of roots
            sage: root_lattice = RootSystem(['A',2,1]).root_lattice()
            sage: root_lattice.simple_root(1).max_coroot_le()
            Traceback (most recent call last):
            ...
            NotImplementedError: Only implemented for finite Cartan type
        """
        if not self.parent().cartan_type().is_finite():
            raise NotImplementedError, "Only implemented for finite Cartan type"
        if not self.is_positive_root():
            raise ValueError, "%s is not in the positive cone of roots"%(self)
        coroots = self.parent().coroot_lattice().positive_roots_by_height(increasing=False)
        for beta in coroots:
            if beta.quantum_root():
                gamma = self - beta.associated_coroot()
                if gamma.is_positive_root():
                    return beta
        return None

    def max_quantum_element(self):
        r"""
        Returns a reduced word for the longest element of the Weyl group whose shortest path in the quantum Bruhat graph to the identity, has sum of quantum coroots at most ``self``.

        INPUT:

        - ``self`` -- an element of the nonnegative integer span of simple roots.

        Really ``self`` is an element of a coroot lattice.

        .. warning::

            This implementation only handles finite Cartan types

        EXAMPLES::

            sage: Qvee = RootSystem(['C',2]).coroot_lattice()
            sage: Qvee.from_vector(vector([1,2])).max_quantum_element()
            [2, 1, 2, 1]
            sage: Qvee.from_vector(vector([1,1])).max_quantum_element()
            [1, 2, 1]
            sage: Qvee.from_vector(vector([0,2])).max_quantum_element()
            [2]

        """
        Qvee = self.parent()
        word = []
        while self != Qvee.zero():
            beta = self.max_coroot_le()
            word += [x for x in beta.associated_reflection()]
            self = self - beta.associated_coroot()
        W = self.parent().weyl_group()
        return (W.demazure_product(word)).reduced_word()

RootSpace.Element = RootSpaceElement
