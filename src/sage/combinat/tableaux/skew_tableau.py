r"""
SkewTableau Element class and subclasses.

See SkewTableaux and its subclasses for the corresponding Parent
classes.

AUTHORS:

- Mike Hansen: Initial version
- Travis Scrimshaw, Arthur Lubovsky (2013-02-11): Factored out
  ``CombinatorialClass``
- Josh Swanson (and others) (2015): tableaux refactoring/cleanup

CLASSES:

.. TODO:: List classes.

Orphaned tests:

    sage: t = SkewTableau([[None, None, 1], [2, 4], [], [3, 4, 5]])
    Traceback (most recent call last):
    ...
    ValueError: Input must be of skew shape

    sage: SkewTableau([[None, 2, 4], [None, 3], [1]]).size()
    4
    sage: SkewTableau([[None, 2], [1, 3]]).size()
    3

    sage: Tableau([[1,2],[3,4]]).to_word_by_row()
    word: 3412
    sage: Tableau([[1, 4, 6], [2, 5], [3]]).to_word_by_row()
    word: 325146

    sage: Tableau([[1,2],[3,4]]).to_word_by_column()
    word: 3142
    sage: Tableau([[1, 4, 6], [2, 5], [3]]).to_word_by_column()
    word: 321546

    sage: Tableau([[1,2],[3,4]]).to_word()
    word: 3412
    sage: Tableau([[1, 4, 6], [2, 5], [3]]).to_word()
    word: 325146
"""
#*****************************************************************************
#       Copyright (C) 2015 Josh Swanson,
#                     2015 Jan Keitel
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#    This code is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    General Public License for more details.
#
#  The full text of the GPL is available at:
#
#                  http://www.gnu.org/licenses/
#*****************************************************************************

import six
from sage.misc.cachefunc import cached_method
from sage.combinat.partition import Partition
from sage.combinat.skew_partition import SkewPartition
from sage.rings.all import ZZ

from sage.combinat.tableaux.bad_shape_tableau import BadShapeTableau

class SkewTableau(BadShapeTableau):
    r"""
    A tableau of skew shape.

    If `\lambda` and `\mu` are two partitions such that
    `\mu \subseteq \lambda`, then a tableau of skew shape
    `\lambda / \mu` means a map that sends the cells of this
    skew shape to some objects. This map "knows" the
    partitions `\lambda` and `\mu`.

    Cell locations are pairs of non-negative integers, though values are
    unrestricted. Cells must form a skew shape.

    TODO: add documentation for the various input formats, as is
    SkewTableaux._element_constructor_.

    EXAMPLES::

        sage: st = SkewTableau([[None, 1],[2,3]]); st
        [[None, 1], [2, 3]]
        sage: st.inner_shape()
        [1]
        sage: st.outer_shape()
        [2, 2]

    EXAMPLES::

        sage: SkewTableau([[None,1],[2,3]])
        [[None, 1], [2, 3]]
        sage: SkewTableau(expr=[[1,1],[[5],[3,4],[1,2]]])
        [[None, 1, 2], [None, 3, 4], [5]]

    The ``expr`` form of a skew tableau consists of the inner partition
    followed by a list of the entries in each row from bottom to top::

        sage: SkewTableau(expr=[[1,1],[[5],[3,4],[1,2]]])
        [[None, 1, 2], [None, 3, 4], [5]]
    """
    _generic_parent = BadShapeTableau._gp(
                      'sage.combinat.tableaux.skew_tableaux',
                      'SkewTableaux')

    def __init__(self, parent, st):
        """
        Note: ``st`` is used as-is. Validation, normalization, etc.
        should be done in the Parent class.

        TESTS::

            sage: st = SkewTableau([[None, 1],[2,3]])
            sage: st = SkewTableau([[None,1,1],[None,2],[4]])
            sage: TestSuite(st).run()

        A skew tableau is immutable, see :trac:`15862`::

            sage: T = SkewTableau([[None,2],[2]])
            sage: t0 = list(T)[0]
            sage: t0[1] = 3
            Traceback (most recent call last):
            ...
            TypeError: 'tuple' object does not support item assignment
            sage: T[0][1] = 5
            Traceback (most recent call last):
            ...
            TypeError: 'SkewTableaux_with_category.element_class' object does not support indexing
        """
        self._set_parent(parent)
        self._st = st

    def __iter__(self):
        return self._st.__iter__()

    def __len__(self):
        r"""
        Returns the number of rows of ``self``.
        
        Note: this differs from the behavior for :class:`BadShapeTableaux`,
        where :meth:`__len__` returns the number of cells.
        """
        return len(self._st)

    @cached_method
    def _dict_unsafe(self):
        d = {(i, j): k for i, row in enumerate(self._st)
                       for j, k in enumerate(row)
                       if k is not None}
        return d

    def to_tuple(self):
        r"""
        Return the tuple of tuples representing the entries of
        ``self``.
        """
        return self._st

    def to_list(self):
        r"""
        Return the list of lists representing the entries of
        ``self``.

        This is a copy of the defining data.

        OUTPUT:

        A list of lists.
        """
        return [list(i) for i in self._st]

    ##################################################################
    ###                       Display Code                         ###
    ##################################################################
    def _repr_(self):
        """
        Return a string representation of ``self``.

        For more on the display options, see
        :obj:`SkewTableaux.global_options`.

        EXAMPLES::

            sage: SkewTableau([[None,2,3],[None,4],[5]])
            [[None, 2, 3], [None, 4], [5]]
        """
        # Automagically calls the correct _repr_* method.
        return self.parent().global_options.dispatch(self, '_repr_', 'display')

    def _repr_list(self):
        """
        Return a string representation of ``self`` as a list of lists.

        EXAMPLES::

            sage: print SkewTableau([[None,2,3],[None,4],[5]])._repr_list()
            [[None, 2, 3], [None, 4], [5]]
        """
        return repr([list(row) for row in self])

    # See #18024. CombinatorialObject provided __str__.
    # Emulate the old functionality. Possibly remove when
    # CombinatorialObject is removed?
    __str__ = _repr_list

    def _repr_diagram(self):
        """
        Return a string representation of ``self`` as a diagram.

        EXAMPLES::

            sage: print SkewTableau([[None,2,3],[None,4],[5]])._repr_diagram()
              .  2  3
              .  4
              5
        """
        none_str = lambda x: "  ." if x is None else "%3s"%str(x)
        if self.parent().global_options('convention') == "French":
            new_rows = ["".join(map(none_str, row)) for row in reversed(self)]
        else:
            new_rows = ["".join(map(none_str, row)) for row in self]
        return '\n'.join(new_rows)

    def _repr_compact(self):
        """
        Return a compact string representation of ``self``.

        EXAMPLES::

            sage: SkewTableau([[None,None,3],[4,5]])._repr_compact()
            '.,.,3/4,5'
            sage: Tableau([])._repr_compact()
            '-'
        """
        if not len(self):
            return '-'
        str_rep = lambda x: '%s'%x if x is not None else '.'
        return '/'.join(','.join(str_rep(r) for r in row) for row in self)

    def pp(self):
        """
        Return a pretty print string of the tableau.

        EXAMPLES::

            sage: SkewTableau([[None,2,3],[None,4],[5]]).pp()
              .  2  3
              .  4
              5
        """
        print self._repr_diagram()

    def _ascii_art_(self):
        """
        TESTS::

            sage: ascii_art(RibbonTableaux([[2,1],[]],[1,1,1],1).list())
            [   1  3    1  2 ]
            [   2   ,   3    ]
        """
        from sage.misc.ascii_art import AsciiArt
        return AsciiArt(self._repr_diagram().splitlines())

    def _latex_(self):
        r"""
        Return a `\LaTeX` representation of ``self``.

        EXAMPLES::

            sage: latex(SkewTableau([[None,2,3],[None,4],[5]]))
            {\def\lr#1{\multicolumn{1}{|@{\hspace{.6ex}}c@{\hspace{.6ex}}|}{\raisebox{-.3ex}{$#1$}}}
            \raisebox{-.6ex}{$\begin{array}[b]{*{3}c}\cline{2-3}
            &\lr{2}&\lr{3}\\\cline{2-3}
            &\lr{4}\\\cline{1-2}
            \lr{5}\\\cline{1-1}
            \end{array}$}
            }
        """
        from sage.combinat.output import tex_from_array
        return tex_from_array(self._st)

    ##################################################################
    ###                      Functionality                         ###
    ##################################################################
    def outer_shape(self):
        """
        Return the outer shape of ``self``.

        EXAMPLES::

            sage: SkewTableau([[None,1,2],[None,3],[4]]).outer_shape()
            [3, 2, 1]
        """
        return Partition(len(row) for row in self)

    def inner_shape(self):
        """
        Return the inner shape of ``self``.

        EXAMPLES::

            sage: SkewTableau([[None,1,2],[None,3],[4]]).inner_shape()
            [1, 1]
            sage: SkewTableau([[1,2],[3,4],[7]]).inner_shape()
            []
            sage: SkewTableau([[None,None,None,2,3],[None,1],[None],[2]]).inner_shape()
            [3, 1, 1]
        """
        return Partition(row.count(None) for row in self)

    def shape(self):
        r"""
        Return the shape of ``self``.

        EXAMPLES::

            sage: SkewTableau([[None,1,2],[None,3],[4]]).shape()
            [3, 2, 1] / [1, 1]
        """
        return SkewPartition([self.outer_shape(), self.inner_shape()])

    def outer_size(self):
        """
        Return the size of the outer shape of ``self``.

        EXAMPLES::

            sage: SkewTableau([[None, 2, 4], [None, 3], [1]]).outer_size()
            6
            sage: SkewTableau([[None, 2], [1, 3]]).outer_size()
            4
        """
        return self.outer_shape().size()

    def inner_size(self):
        """
        Return the size of the inner shape of ``self``.

        EXAMPLES::

            sage: SkewTableau([[None, 2, 4], [None, 3], [1]]).inner_size()
            2
            sage: SkewTableau([[None, 2], [1, 3]]).inner_size()
            1
        """
        return self.inner_shape().size()

    def conjugate(self):
        """
        Return the conjugate of ``self``.

        EXAMPLES::

            sage: SkewTableau([[None,1],[2,3]]).conjugate()
            [[None, 2], [1, 3]]
        """
        conj_shape = self.outer_shape().conjugate()

        conj = [[None]*row_length for row_length in conj_shape]

        for i in range(len(conj)):
            conj_i = conj[i]
            for j in range(len(conj_i)):
                conj_i[j] = self._st[j][i]

        return self.__class__(conj)

    def weight(self):
        """
        Return the weight (aka evaluation) of the tableau ``self``.

        The weight of a skew tableau `T` is the list
        `[a_1, a_2, a_3, \ldots, a_m]`, where `a_k` is the number of
        entries of `T` equal to `k` and `a_m` is the last non-zero
        entry.

        The weight of a skew tableau `T` is the same as the weight
        of the reading word of `T`, for any reading order.

        :meth:`evaluation` is a synonym for this method.

        EXAMPLES::

            sage: SkewTableau([[1,2],[3,4]]).weight()
            [1, 1, 1, 1]

            sage: SkewTableau([[None,2],[None,4],[None,5],[None]]).weight()
            [0, 1, 0, 1, 1]

            sage: SkewTableau([]).weight()
            []

            sage: SkewTableau([[None,None,None],[None]]).weight()
            []

            sage: SkewTableau([[None,3,4],[None,6,7],[4,8],[5,13],[6],[7]]).weight()
            [0, 0, 1, 2, 1, 2, 2, 1, 0, 0, 0, 0, 1]

        TESTS:

        We check that this agrees with going to the word::

            sage: t = SkewTableau([[None,None,4,7,15],[6,2,16],[2,3,19],[4,5],[7]])
            sage: def by_word(T):
            ....:     ed = T.to_word().evaluation_dict()
            ....:     m = max(ed.keys()) + 1
            ....:     return [ed.get(k,0) for k in range(1,m)]
            sage: by_word(t) == t.weight()
            True
            sage: SST = SemistandardTableaux(shape=[3,1,1])
            sage: all(by_word(t) == SkewTableau(t).weight() for t in SST)
            True
        """
        d = self.weight_dict()
        if not d:
            return []
        ret = [0]*max(d)
        for k, v in six.iteritems(d):
            ret[k-1] = v
        return ret

    # Alias
    evaluation = weight

    def filling(self):
        """
        Return a list of lists of the non-empty entries in ``self``.

        EXAMPLES::

            sage: t = SkewTableau([[None,1],[2,3]])
            sage: t.filling()
            [[1], [2, 3]]
        """
        return [[i for i in row if i is not None] for row in self]

    def is_row_increasing(self):
        """
        Return ``True`` if the entries of the rows of ``self`` are
        weakly increasing and ``False`` otherwise.
        """
        return all( row[i]<=row[i+1] for row in self.rows()
                                     for i in range(len(row)-1) )

    def is_row_strict(self):
        """
        Return ``True`` if the entries of the rows of ``self`` are
        strictly increasing and ``False`` otherwise.

        EXAMPLES::

            sage: Tableau([[1, 3], [2, 4]]).is_row_strict()
            True
            sage: Tableau([[1, 2], [2, 4]]).is_row_strict()
            True
            sage: Tableau([[2, 3], [2, 4]]).is_row_strict()
            True
            sage: Tableau([[5, 3], [2, 4]]).is_row_strict()
            False
        """
        return all( row[i]<row[i+1] for row in self.rows()
                                    for i in range(len(row)-1) )

    def is_column_increasing(self):
        """
        Return ``True`` if the entries of the columns of ``self`` are
        weakly increasing and ``False`` otherwise.
        """
        return all( col[i]<=col[i+1] for col in self.columns()
                                     for i in range(len(col)-1) )

    def is_column_strict(self):
        """
        Return ``True`` if the entries of the columns of ``self`` are
        strictly increasing and ``False`` otherwise.

        EXAMPLES::

            sage: Tableau([[1, 3], [2, 4]]).is_column_strict()
            True
            sage: Tableau([[1, 2], [2, 4]]).is_column_strict()
            True
            sage: Tableau([[2, 3], [2, 4]]).is_column_strict()
            False
            sage: Tableau([[5, 3], [2, 4]]).is_column_strict()
            False
            sage: Tableau([]).is_column_strict()
            True
            sage: Tableau([[1, 4, 2]]).is_column_strict()
            True
            sage: Tableau([[1, 4, 2], [2, 5]]).is_column_strict()
            True
            sage: Tableau([[1, 4, 2], [2, 3]]).is_column_strict()
            False
        """
        return all( col[i]<col[i+1] for col in self.columns()
                                     for i in range(len(col)-1) )

    def is_increasing(self):
        """
        Return ``True`` if ``self`` is an increasing tableau and
        ``False`` otherwise.

        A tableau is increasing if it is both row strict and column strict.

        EXAMPLES::

            sage: Tableau([[1, 3], [2, 4]]).is_increasing()
            True
            sage: Tableau([[1, 2], [2, 4]]).is_increasing()
            True
            sage: Tableau([[2, 3], [2, 4]]).is_increasing()
            False
            sage: Tableau([[5, 3], [2, 4]]).is_increasing()
            False
            sage: Tableau([[1, 2, 3], [2, 3], [3]]).is_increasing()
            True
        """
        return self.is_row_strict() and self.is_column_strict()

    def is_standard(self):
        """
        Return ``True`` if ``self`` is a standard skew tableau and ``False``
        otherwise.
        
        A skew tableaux is standard if it is row strict, column strict,
        and uses each entry from 1 to its size exactly once.

        EXAMPLES::

            sage: SkewTableau([[None, 2], [1, 3]]).is_standard()
            True
            sage: SkewTableau([[None, 2], [2, 4]]).is_standard()
            False
            sage: SkewTableau([[None, 3], [2, 4]]).is_standard()
            False
            sage: SkewTableau([[None, 2], [2, 4]]).is_standard()
            False
        """
        return (self.is_increasing() and
                sorted(self.iter_entries()) == range(1, self.size()+1) )

    def is_semistandard(self):
        """
        Return ``True`` if ``self`` is a semistandard skew tableau and
        ``False`` otherwise.
        
        A skew tableaux is semistandard if it is column strict and increasing
        (weakly) along rows.

        EXAMPLES::

            sage: SkewTableau([[None, 2, 2], [1, 3]]).is_semistandard()
            True
            sage: SkewTableau([[None, 2], [2, 4]]).is_semistandard()
            True
            sage: SkewTableau([[None, 3], [2, 4]]).is_semistandard()
            True
            sage: SkewTableau([[None, 2], [1, 2]]).is_semistandard()
            False
            sage: SkewTableau([[None, 2, 3]]).is_semistandard()
            True
            sage: SkewTableau([[None, 3, 2]]).is_semistandard()
            False
            sage: SkewTableau([[None, 2, 3], [1, 4]]).is_semistandard()
            True
            sage: SkewTableau([[None, 2, 3], [1, 2]]).is_semistandard()
            False
            sage: SkewTableau([[None, None, 3], [None, 2, 3]]).is_semistandard()
            False
        """
        return self.is_column_strict() and self.is_row_increasing()

    def is_ribbon(self):
        r"""
        Return ``True`` if and only if the shape of ``self`` is a
        ribbon, that is, if it has exactly one cell in each of `q`
        consecutive diagonals for some nonnegative integer `q`.

        EXAMPLES::

            sage: S=SkewTableau([[None, None, 1, 2],[None, None, 3],[1, 3, 4]])
            sage: S.pp()
              .  .  1  2
              .  .  3
              1  3  4
            sage: S.is_ribbon()
            True

            sage: S=SkewTableau([[None, 1, 1, 2],[None, 2, 3],[1, 3, 4]])
            sage: S.pp()
              .  1  1  2
              .  2  3
              1  3  4
            sage: S.is_ribbon()
            False

            sage: S=SkewTableau([[None, None, 1, 2],[None, None, 3],[1]])
            sage: S.pp()
              .  .  1  2
              .  .  3
              1
            sage: S.is_ribbon()
            False

            sage: S=SkewTableau([[None, None, None, None],[None, None, 3],[1, 2, 4]])
            sage: S.pp()
              .  .  .  .
              .  .  3
              1  2  4
            sage: S.is_ribbon()
            True

            sage: S=SkewTableau([[None, None, None, None],[None, None, 3],[None, 2, 4]])
            sage: S.pp()
              .  .  .  .
              .  .  3
              .  2  4
            sage: S.is_ribbon()
            True

            sage: S=SkewTableau([[None, None],[None]])
            sage: S.pp()
              .  .
              .
            sage: S.is_ribbon()
            True

        """
        if not self.size():
            return True

        from collections import Counter
        content_counts = Counter(i - j for i,j in self.iter_cells())
        
        # Ensure no more than one entry is on each diagonal
        if any(count > 1 for count in six.itervalues(content_counts)):
            return False
        
        # Ensure all entries are consecutive
        content_counts = sorted(content for content, count
                                  in six.iteritems(content_counts)
                                  if count > 0)
        return content_counts == range(content_counts[0], content_counts[-1]+1)


    def is_k_tableau(self, k):
        r"""
        Checks whether ``self`` is a valid skew weak `k`-tableau.

        EXAMPLES::

            sage: t = SemistandardSkewTableau([[None,2,3],[2,3],[3]])
            sage: t.is_k_tableau(3)
            True
            sage: t = SemistandardSkewTableau([[None,1,3],[2,2],[3]])
            sage: t.is_k_tableau(3)
            False
        """
        shapes = self.to_chain()
        kshapes = [ la.k_conjugate(k) for la in shapes ]
        return all( kshapes[i+1].contains(kshapes[i]) for i in range(len(shapes)-1) )

    def to_expr(self):
        """
        The first list in a result corresponds to the inner partition of
        the skew shape. The second list is a list of the rows in the skew
        tableau read from the bottom up.

        Provided for compatibility with MuPAD-Combinat. In MuPAD-Combinat,
        if ``t`` is a skew tableau, then to_expr gives the same result as
        ``expr(t)`` would give in MuPAD-Combinat.

        EXAMPLES::

            sage: SkewTableau([[None,1,1,3],[None,2,2],[1]]).to_expr()
            [[1, 1], [[1], [2, 2], [1, 1, 3]]]
            sage: SkewTableau([]).to_expr()
            [[], []]
        """
        rows = self.filling()
        rows.reverse()
        return [self.inner_shape(), rows]

    def to_tableau(self):
        """
        Returns a :class:`Tableau` with the same filling.
        
        This only works if the inner shape of the skew tableau has size
        zero. TODO: add failing example.

        EXAMPLES::

            sage: SkewTableau([[1,2],[3,4]]).to_tableau()
            [[1, 2], [3, 4]]
        """
        if self.inner_size() != 0:
            raise ValueError("the inner size of the skew tableau must be 0")
        else:
            # TODO: make this use the new tableaux
            #from sage.combinat.tableaux.straight_tableau import Tableau
            from sage.combinat.tableau import Tableau
            return Tableau(self)

    def to_ribbon(self, check_input=True):
        """
        Return ``self`` as a ribbon-shaped tableau
        (:class:`~sage.combinat.ribbon_shaped_tableau.RibbonShapedTableau`),
        provided that the shape of ``self`` is a ribbon.

        INPUT:

        - ``check_input`` -- (default: ``True``) whether or not to check
          that ``self`` indeed has ribbon shape

        EXAMPLES::

            sage: SkewTableau([[None,1],[2,3]]).to_ribbon()
            [[None, 1], [2, 3]]
        """
        # TODO: clean up after ribbon tableau have been looked into
        if check_input and not self.is_ribbon():
            raise ValueError("self must be a ribbon")
        from sage.combinat.ribbon_shaped_tableau import RibbonShapedTableau
        r = [[i for i in row if i is not None] for row in self]
        return RibbonShapedTableau(r)

class SemistandardSkewTableau(SkewTableau):
    r"""
    A semistandard tableau of skew shape.

    See :class:`SkewTableau` for more details and construction options
    These tableau are in addition semistandard, meaning they are weakly
    increasing along rows and strictly increasing along columns. We
    frequently imagine their entries are non-negative integers, though this
    is not strictly enforced.
    """
    _generic_parent = SkewTableau._gp(
                      'sage.combinat.tableaux.skew_tableaux',
                      'SemistandardSkewTableaux')

    def slide(self, corner=None):
        """
        Apply a jeu-de-taquin slide to ``self`` on the specified corner and
        returns the new tableau.
        
        If no corner is given an arbitrary corner is chosen. See [FW]_ p12-13.

        EXAMPLES::

            sage: st = SemistandardSkewTableau([[None, None, None, None,2],[None, None, None, None,6], [None, 2, 4, 4], [2, 3, 6], [5,5]])
            sage: st.slide((2,0))
            [[None, None, None, None, 2], [None, None, None, None, 6], [2, 2, 4, 4], [3, 5, 6], [5]]

        TESTS::

            sage: st
            [[None, None, None, None, 2], [None, None, None, None, 6], [None, 2, 4, 4], [2, 3, 6], [5, 5]]
        """
        new_st = self.to_list()
        inner_corners = self.inner_shape().corners()
        outer_corners = self.outer_shape().corners()
        if corner is not None:
            if tuple(corner) not in inner_corners:
                raise ValueError("corner must be an inner corner")
        else:
            if not inner_corners:
                return self
            else:
                corner = inner_corners[0]

        spotl, spotc = corner
        while (spotl, spotc) not in outer_corners:
            # Check to see if there is nothing to the right
            if spotc == len(new_st[spotl]) - 1:
                # Swap the hole with the cell below
                new_st[spotl][spotc] = new_st[spotl+1][spotc]
                new_st[spotl+1][spotc] = None
                spotl += 1
                continue

            # Check to see if there is nothing below
            if (spotl == len(new_st) - 1) or (len(new_st[spotl+1]) <= spotc):
                # Swap the hole with the cell to the right
                new_st[spotl][spotc] = new_st[spotl][spotc+1]
                new_st[spotl][spotc+1] = None
                spotc += 1
                continue

            # If we get to this stage, we need to compare
            below = new_st[spotl+1][spotc]
            right = new_st[spotl][spotc+1]
            if below <= right:
                # Swap with the cell below
                new_st[spotl][spotc] = new_st[spotl+1][spotc]
                new_st[spotl+1][spotc] = None
                spotl += 1
                continue
            else:
                # Swap with the cell to the right
                new_st[spotl][spotc] = new_st[spotl][spotc+1]
                new_st[spotl][spotc+1] = None
                spotc += 1
                continue

        # Clean up to remove the "None" at an outside corner
        # Remove the last row if there is nothing left in it
        new_st[spotl].pop()
        if len(new_st[spotl]) == 0:
            new_st.pop()

        return self.__class__(new_st)

    def rectify(self):
        """
        Return a :class:`Tableau` formed by applying the jeu de taquin
        process to ``self``. See page 15 of [FW]_.

        REFERENCES:

        .. [FW] William Fulton,
           *Young Tableaux*,
           Cambridge University Press 1997.

        EXAMPLES::

            sage: s = SemistandardSkewTableau([[None,1],[2,3]])
            sage: s.rectify()
            [[1, 3], [2]]
            sage: SemistandardSkewTableau([[None, None, None, 4],[None,None,1,6],[None,None,5],[2,3]]).rectify()
            [[1, 3, 4, 6], [2, 5]]

        TESTS::

            sage: s
            [[None, 1], [2, 3]]
        """
        rect = self
        inner_corners = rect.inner_shape().corners()

        while len(inner_corners) > 0:
            rect = rect.slide()
            inner_corners = rect.inner_shape().corners()

        return rect.to_tableau()

    def standardization(self, check=True):
        r"""
        Return the standardization of ``self``.

        The standardization of a semistandard skew tableau `T` is the standard
        skew tableau `\mathrm{st}(T)` of the same shape as `T` whose
        reversed reading word is the standardization of the reversed reading
        word of `T`.

        The standardization of a word `w` can be formed by replacing all `1`'s
        in `w` by `1, 2, \ldots, k_1` from left to right, all `2`'s in `w` by
        `k_1 + 1, k_1 + 2, \ldots, k_2`, and repeating for all letters that
        appear in `w`.
        See also :meth:`Word.standard_permutation()`.

        INPUT:

        - ``check`` -- (Default: ``True``) Check to make sure ``self`` is
          semistandard. Set to ``False`` to avoid this check.

        EXAMPLES::

            sage: t = SemistandardSkewTableau([[None,None,3,4,7,19],[None,4,4,8],[None,5,16,17],[None],[2],[3]])
            sage: t.standardization()
            [[None, None, 3, 6, 8, 12], [None, 4, 5, 9], [None, 7, 10, 11], [None], [1], [2]]

        Standard skew tableaux are fixed under standardization::

            sage: p = Partition([4,3,3,2])
            sage: q = Partitions(3).random_element()
            sage: all((t == t.standardization() for t in StandardSkewTableaux([p, q])))
            True

        The reading word of the standardization is the
        standardization of the reading word::

            sage: t = SemistandardSkewTableau([[None,3,4,4],[None,6,10],[7,7,11],[18]])
            sage: t.to_word().standard_permutation() == t.standardization().to_permutation()
            True

        TESTS:

        Some corner cases::

            sage: t = SemistandardSkewTableau([[None,None],[None]])
            sage: t.standardization()
            [[None, None], [None]]
            sage: t = SemistandardSkewTableau([])
            sage: t.standardization()
            []
        """
        # Can skip the check since we're already semistandard.
        return StandardSkewTableau(check=False, shape_word=(
                   self.shape(),
                   self.to_word_by_row().standard_permutation()) )

    def bender_knuth_involution(self, k, rows=None):
        r"""
        Return the image of ``self`` under the `k`-th Bender--Knuth
        involution.

        Let `T` be a tableau, then a *lower free `k` in `T`* means a cell of
        `T` which is filled with the integer `k` and whose direct lower
        neighbor is not filled with the integer `k + 1` (in particular,
        this lower neighbor might not exist at all). Let an *upper free `k + 1`
        in `T`* mean a cell of `T` which is filled with the integer `k + 1`
        and whose direct upper neighbor is not filled with the integer `k`
        (in particular, this neighbor might not exist at all). It is clear
        that for any row `r` of `T`, the lower free `k`'s and the upper
        free `k + 1`'s in `r` together form a contiguous interval or `r`.

        The *`k`-th Bender--Knuth switch at row `i`* changes the entries of
        the cells in this interval in such a way that if it used to have
        `a` entries of `k` and `b` entries of `k + 1`, it will now
        have `b` entries of `k` and `a` entries of `k + 1`. For fixed `k`, the
        `k`-th Bender--Knuth switches for different `i` commute. The
        composition of the `k`-th Bender--Knuth switches for all rows is
        called the *`k`-th Bender--Knuth involution*. This is used to show that
        the Schur functions defined by semistandard (skew) tableaux are
        symmetric functions.

        INPUT:

        - ``k`` -- an integer

        - ``rows`` -- (Default ``None``) When set to ``None``, the method
          computes the `k`-th Bender--Knuth involution as defined above.
          When an iterable, this computes the composition of the `k`-th
          Bender--Knuth switches at row `i` over all `i` in ``rows``. When set
          to an integer `i`, the method computes the `k`-th Bender--Knuth
          switch at row `i`. Note the indexing of the rows starts with `1`.

        - ``check`` -- (Default: ``True``) Check to make sure ``self`` is
          semistandard. Set to ``False`` to avoid this check.

        OUTPUT:

        The image of ``self`` under either the `k`-th Bender--Knuth
        involution, the `k`-th Bender--Knuth switch at a certain row, or
        the composition of such switches, as detailed in the INPUT section.

        EXAMPLES::

            sage: t = SemistandardSkewTableau([[None,None,None,4,4,5,6,7],[None,2,4,6,7,7,7],[None,4,5,8,8,9],[None,6,7,10],[None,8,8,11],[None],[4]])
            sage: t
            [[None, None, None, 4, 4, 5, 6, 7], [None, 2, 4, 6, 7, 7, 7], [None, 4, 5, 8, 8, 9], [None, 6, 7, 10], [None, 8, 8, 11], [None], [4]]
            sage: t.bender_knuth_involution(1)
            [[None, None, None, 4, 4, 5, 6, 7], [None, 1, 4, 6, 7, 7, 7], [None, 4, 5, 8, 8, 9], [None, 6, 7, 10], [None, 8, 8, 11], [None], [4]]
            sage: t.bender_knuth_involution(4)
            [[None, None, None, 4, 5, 5, 6, 7], [None, 2, 4, 6, 7, 7, 7], [None, 5, 5, 8, 8, 9], [None, 6, 7, 10], [None, 8, 8, 11], [None], [5]]
            sage: t.bender_knuth_involution(5)
            [[None, None, None, 4, 4, 5, 6, 7], [None, 2, 4, 5, 7, 7, 7], [None, 4, 6, 8, 8, 9], [None, 5, 7, 10], [None, 8, 8, 11], [None], [4]]
            sage: t.bender_knuth_involution(6)
            [[None, None, None, 4, 4, 5, 6, 6], [None, 2, 4, 6, 6, 7, 7], [None, 4, 5, 8, 8, 9], [None, 6, 7, 10], [None, 8, 8, 11], [None], [4]]
            sage: t.bender_knuth_involution(666) == t
            True
            sage: t.bender_knuth_involution(4, 2) == t
            True
            sage: t.bender_knuth_involution(4, 3)
            [[None, None, None, 4, 4, 5, 6, 7], [None, 2, 4, 6, 7, 7, 7], [None, 5, 5, 8, 8, 9], [None, 6, 7, 10], [None, 8, 8, 11], [None], [4]]

        The Bender--Knuth involution is an involution::

            sage: t = SemistandardSkewTableau([[None,3,4,4],[None,6,10],[7,7,11],[18]])
            sage: all(t.bender_knuth_involution(k).bender_knuth_involution(k) == t for k in range(1,4))
            True

        The same for the single switches::

            sage: all(t.bender_knuth_involution(k, j).bender_knuth_involution(k, j) == t for k in range(1,5) for j in range(1, 5))
            True

        Locality of the Bender--Knuth involutions::

            sage: all(t.bender_knuth_involution(k).bender_knuth_involution(l) == t.bender_knuth_involution(l).bender_knuth_involution(k) for k in range(1,5) for l in range(1,5) if abs(k - l) > 1)
            True

        Coxeter relation of the Bender--Knuth involutions (they have the form
        `(ab)^6 = 1`)::

            sage: p = lambda t, k: t.bender_knuth_involution(k).bender_knuth_involution(k + 1)
            sage: all(p(p(p(p(p(p(t,k),k),k),k),k),k) == t for k in range(1,5))
            True

        TESTS::

            sage: t = SemistandardSkewTableau([])
            sage: t.bender_knuth_involution(3)
            []
            sage: t = SemistandardSkewTableau([[None,None],[None]])
            sage: t.bender_knuth_involution(3)
            [[None, None], [None]]

        AUTHORS:

        - Darij Grinberg (2013-05-14)
        """
        l = len(self)    # l is the number of rows of self.
        # Sanitizing the rows input so that it always becomes a list of
        # nonnegative integers. We also subtract 1 from these integers
        # because the i-th row of a tableau T is T[i - 1].
        if rows is None:
            rows = range(l)
        elif rows in ZZ:
            rows = [rows - 1]
        else:
            rows = [i - 1 for i in rows]
        # Now, rows should be iterable.

        # result_tab is going to be the result tableau (as a list of lists);
        # we will build it up step by step, starting with a deep copy of self.
        result_tab = [list(row) for row in self]
        for i in rows:
            if i >= l:
                continue
            # Setup the previous and next rows
            if i == 0:
                prev_row = [None] * len(result_tab[i])
            else:
                prev_row = result_tab[i-1]
            if i == l - 1:
                next_row = [None] * len(result_tab[i])
            else:
                next_row = result_tab[i+1] + [None] * (len(result_tab[i]) - len(result_tab[i+1]))
            a = 0
            b = 0
            sk = None # The first entry of k
            sk1 = None # The first entry of k+1
            for j, val in enumerate(result_tab[i]):
                if val == k and next_row[j] != k + 1:
                    if sk is None:
                        sk = j
                    a += 1
                elif val == k + 1 and prev_row[j] != k:
                    if sk1 is None:
                        sk1 = j
                    b += 1
            if sk1 is not None:
                if a > b:
                    for j in range(sk1-(a-b), sk1):
                        result_tab[i][j] = k + 1
                elif a < b:
                    for j in range(sk1, sk1+b-a):
                        result_tab[i][j] = k
            elif sk is not None:
                for j in range(sk, sk+a):
                    result_tab[i][j] = k + 1

        return self.__class__(result_tab)

    def restrict(self, n):
        """
        Return the restriction of the semistandard skew
        tableau to all the entries less than or equal to ``n``.

        .. NOTE::

            If only the outer shape of the restriction, rather than
            the whole restriction, is needed, then the faster method
            :meth:`restriction_outer_shape` is preferred. Similarly if
            only the skew shape is needed, use :meth:`restriction_shape`.

        EXAMPLES::

            sage: SemistandardSkewTableau([[None,1],[2],[3]]).restrict(2)
            [[None, 1], [2]]
            sage: SemistandardSkewTableau([[None,1],[2],[3]]).restrict(1)
            [[None, 1]]
            sage: SemistandardSkewTableau([[None,1],[1],[2]]).restrict(1)
            [[None, 1], [1]]
        """
        return self.__class__((x for x in row if x is None or x <= n)
                                 for row in self)

    def restriction_outer_shape(self, n):
        """
        Return the outer shape of the restriction of the
        semistandard skew tableau ``self`` to `n`.

        See :meth:`restrict` for further information.

        EXAMPLES::

            sage: SemistandardSkewTableau([[None,None],[2,3],[3,4]]).restriction_outer_shape(3)
            [2, 2, 1]
            sage: SemistandardSkewTableau([[None,2],[None],[4],[5]]).restriction_outer_shape(2)
            [2, 1]
            sage: T = SemistandardSkewTableau([[None,None,3,5],[None,4,4],[17]])
            sage: T.restriction_outer_shape(0)
            [2, 1]
            sage: T.restriction_outer_shape(2)
            [2, 1]
            sage: T.restriction_outer_shape(3)
            [3, 1]
            sage: T.restriction_outer_shape(4)
            [3, 3]
            sage: T.restriction_outer_shape(19)
            [4, 3, 1]
        """
        from sage.combinat.partition import Partition
        return Partition(sum(1 for x in row if x is None or x <= n)
                         for row in self)

    def restriction_shape(self, n):
        """
        Return the skew shape of the restriction of the semistandard
        skew tableau ``self`` to ``n``.

        See :meth:`restrict` for further information.

        EXAMPLES::

            sage: SemistandardSkewTableau([[None,None],[2,3],[3,4]]).restriction_shape(3)
            [2, 2, 1] / [2]
            sage: SemistandardSkewTableau([[None,2],[None],[4],[5]]).restriction_shape(2)
            [2, 1] / [1, 1]
            sage: T = SemistandardSkewTableau([[None,None,3,5],[None,4,4],[17]])
            sage: T.restriction_shape(0)
            [2, 1] / [2, 1]
            sage: T.restriction_shape(2)
            [2, 1] / [2, 1]
            sage: T.restriction_shape(3)
            [3, 1] / [2, 1]
            sage: T.restriction_shape(4)
            [3, 3] / [2, 1]
        """
        return SkewPartition([self.restriction_outer_shape(n), self.inner_shape()])

    def to_chain(self, max_entry=None):
        """
        Return the chain of partitions making up the skew tableau ``self``.

        See :meth:`restrict` for further information.

        The optional keyword parameter ``max_entry`` can be used to
        customize the length of the chain. Specifically, if this parameter
        is set to a nonnegative integer ``n``, then the chain is
        constructed from the positions of the letters `1, 2, \ldots, n`
        in the tableau.

        EXAMPLES::

            sage: SemistandardSkewTableau([[None,1],[2],[3]]).to_chain()
            [[1], [2], [2, 1], [2, 1, 1]]
            sage: SemistandardSkewTableau([[None,1],[1],[2]]).to_chain()
            [[1], [2, 1], [2, 1, 1]]
            sage: SemistandardSkewTableau([[None,1],[1],[2]]).to_chain(max_entry=2)
            [[1], [2, 1], [2, 1, 1]]
            sage: SemistandardSkewTableau([[None,1],[1],[2]]).to_chain(max_entry=3)
            [[1], [2, 1], [2, 1, 1], [2, 1, 1]]
            sage: SemistandardSkewTableau([[None,1],[1],[2]]).to_chain(max_entry=1)
            [[1], [2, 1]]
            sage: SemistandardSkewTableau([[None,None,2],[None,3],[None,5]]).to_chain(max_entry=6)
            [[2, 1, 1], [2, 1, 1], [3, 1, 1], [3, 2, 1], [3, 2, 1], [3, 2, 2], [3, 2, 2]]
            sage: SemistandardSkewTableau([]).to_chain()
            [[]]
            sage: SemistandardSkewTableau([]).to_chain(max_entry=1)
            [[], []]

        TESTS:

        Check that :meth:`to_chain()` does not skip letters::

            sage: t = SemistandardSkewTableau([[None, 2, 3], [3]])
            sage: t.to_chain()
            [[1], [1], [2], [3, 1]]

            sage: T = SemistandardSkewTableau([[None]])
            sage: T.to_chain()
            [[1]]
        """
        if max_entry is None:
            if not self.size():
                max_entry = 0
            else:
                max_entry = max(self.iter_entries())
        return [self.restriction_outer_shape(n) for n in range(max_entry+1)]

class StandardSkewTableau(SemistandardSkewTableau):
    r"""
    A standard tableau of skew shape.

    See :class:`SkewTableau` for more details and construction options.
    These tableau are in addition standard, meaning they are strictly
    increasing along rows and columns, and they use entries from 1
    through the size of the tableau precisely once each.
    """
    _generic_parent = SkewTableau._gp(
                      'sage.combinat.tableaux.skew_tableaux',
                      'StandardSkewTableaux')

    def to_permutation(self):
        """
        Return a permutation with the entries of ``self`` obtained by reading
        ``self`` row by row, from the bottommost to the topmost row, with
        each row being read from left to right, in English convention.
        See :meth:`to_word_by_row()`.

        EXAMPLES::

            sage: StandardSkewTableau([[None, None,2],[None, 3,4],[None],[1]]).to_permutation()
            [1, 3, 4, 2]
            sage: StandardSkewTableau([[None,2],[None,4],[1],[3]]).to_permutation()
            [3, 1, 4, 2]
            sage: StandardSkewTableau([[None]]).to_permutation()
            []
        """
        from sage.combinat.permutation import Permutation
        return Permutation(i for row in reversed(list(self))
                             for i in row
                             if i is not None)
