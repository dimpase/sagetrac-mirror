r"""
Finitely generated magmas
"""
#*****************************************************************************
#  Copyright (C) 2014 Nicolas M. Thiery <nthiery at users.sf.net>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
#******************************************************************************

from sage.misc.abstract_method import abstract_method
from sage.categories.category_with_axiom import CategoryWithAxiom
from sage.categories.magmas import Magmas

class FinitelyGeneratedMagmas(CategoryWithAxiom):
    r"""
    The category of finitely generated (multiplicative) magmas.

    See :meth:`Magmas.SubcategoryMethods.FinitelyGeneratedAsMagma` for
    details.

    EXAMPLES::

        sage: C = Magmas().FinitelyGeneratedAsMagma(); C
        Category of finitely generated magmas
        sage: C.super_categories()
        [Category of magmas]
        sage: sorted(C.axioms())
        ['FinitelyGeneratedAsMagma']

    TESTS::

        sage: TestSuite(C).run()
    """

    _base_category_class_and_axiom = (Magmas, "FinitelyGeneratedAsMagma")

    class ParentMethods:

        @abstract_method
        def magma_generators(self):
            """
            Return distinguished magma generators for ``self``.

            OUTPUT: a finite family

            This method should be implemented by all
            :class:`finitely generated magmas <FinitelyGeneratedMagmas>`_.

            EXAMPLES::

                sage: S = FiniteSemigroups().example()
                sage: S.magma_generators()
                Family ('a', 'b', 'c', 'd')
            """

        # TODO: update transitive ideal
        def succ_generators(self, side="twosided"):
            r"""
            Return the successor function of the ``side``-sided Cayley
            graph of ``self``.

            This is a function that maps an element of ``self`` to all
            the products of ``x`` by a generator of this finitely
            generated magma, where the product is taken on the left,
            right, or both sides.

            INPUT:

            - ``side``: "left", "right", or "twosided"

            FIXME: find a better name for this method
            FIXME: should we return a set? a family?

            EXAMPLES::

                sage: S = FiniteSemigroups().example()
                sage: S.succ_generators("left" )(S('ca'))
                ('ac', 'bca', 'ca', 'dca')
                sage: S.succ_generators("right")(S('ca'))
                ('ca', 'cab', 'ca', 'cad')
                sage: S.succ_generators("twosided" )(S('ca'))
                ('ac', 'bca', 'ca', 'dca', 'ca', 'cab', 'ca', 'cad')

            """
            left  = (side == "left"  or side == "twosided")
            right = (side == "right" or side == "twosided")
            generators = self.magma_generators()
            return lambda x: (tuple(g * x for g in generators) if left  else ()) + (tuple(x * g for g in generators) if right else ())

        def ideal(self, gens, side="twosided"):
            r"""
            Return the ``side``-sided ideal generated by ``gens``.

            This brute force implementation recursively multiplies the
            elements of ``gens`` by the distinguished generators of
            this finitely generated magma.

            .. SEEALSO:: :meth:`magma_generators`

            INPUT:

            - ``gens`` -- a list (or iterable) of elements of ``self``
            - ``side`` -- [default: "twosided"] "left", "right" or "twosided"

            EXAMPLES::

                sage: S = FiniteSemigroups().example()
                sage: list(S.ideal([S('cab')], side="left"))
                ['cab', 'dcab', 'adcb', 'acb', 'bdca', 'bca', 'abdc',
                'cadb', 'acdb', 'bacd', 'abcd', 'cbad', 'abc', 'acbd',
                'dbac', 'dabc', 'cbda', 'bcad', 'cabd', 'dcba',
                'bdac', 'cba', 'badc', 'bac', 'cdab', 'dacb', 'dbca',
                'cdba', 'adbc', 'bcda']
                sage: list(S.ideal([S('cab')], side="right"))
                ['cab', 'cabd']
                sage: list(S.ideal([S('cab')], side="twosided"))
                ['cab', 'dcab', 'acb', 'adcb', 'acbd', 'bdca', 'bca',
                'cabd', 'abdc', 'cadb', 'acdb', 'bacd', 'abcd', 'cbad',
                'abc', 'dbac', 'dabc', 'cbda', 'bcad', 'dcba', 'bdac',
                'cba', 'cdab', 'bac', 'badc', 'dacb', 'dbca', 'cdba',
                'adbc', 'bcda']
                sage: list(S.ideal([S('cab')]))
                ['cab', 'dcab', 'acb', 'adcb', 'acbd', 'bdca', 'bca',
                'cabd', 'abdc', 'cadb', 'acdb', 'bacd', 'abcd', 'cbad',
                'abc', 'dbac', 'dabc', 'cbda', 'bcad', 'dcba', 'bdac',
                'cba', 'cdab', 'bac', 'badc', 'dacb', 'dbca', 'cdba',
                'adbc', 'bcda']

            """
            from sage.combinat.backtrack import TransitiveIdeal
            return TransitiveIdeal(self.succ_generators(side = side), gens)

        def __iter__(self):
            r"""
            Return an iterator over the elements of ``self``.

            This brute force implementation recursively multiplies
            together the magma generators.

            .. SEEALSO:: :meth:`magma_generators`

            EXAMPLES::

                sage: S = FiniteSemigroups().example(alphabet=('x','y'))
                sage: it = S.__iter__()
                sage: list(it)
                ['y', 'x', 'xy', 'yx']
            """
            return self.ideal(self.magma_generators(), side="right")
