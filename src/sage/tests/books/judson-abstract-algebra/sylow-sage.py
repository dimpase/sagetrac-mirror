##      -*-   coding: utf-8   -*-     ##
##          Sage Doctest File         ##
#**************************************#
#*    Generated from PreTeXt source   *#
#*    on 2017-08-26T21:16:30-07:00    *#
#*                                    *#
#*   http://mathbook.pugetsound.edu   *#
#*                                    *#
#**************************************#
##
"""
Please contact Rob Beezer (beezer@ups.edu) with
any test failures here that need to be changed
as a result of changes accepted into Sage.  You
may edit/change this file in any sensible way, so
that development work may procede.  Your changes
may later be replaced by the authors of "Abstract
Algebra: Theory and Applications" when the text is
updated, and a replacement of this file is proposed
for review.
"""
##
## To execute doctests in these files, run
##   $ $SAGE_ROOT/sage -t <directory-of-these-files>
## or
##   $ $SAGE_ROOT/sage -t <a-single-file>
##
## Replace -t by "-tp n" for parallel testing,
##   "-tp 0" will use a sensible number of threads
##
## See: http://www.sagemath.org/doc/developer/doctesting.html
##   or run  $ $SAGE_ROOT/sage --advanced  for brief help
##
## Generated at 2017-08-26T21:16:30-07:00
## From "Abstract Algebra"
## At commit 26d3cac0b4047f4b8d6f737542be455606e2c4b4
##
## Section 15.6 Sage
##
r"""
~~~~~~~~~~~~~~~~~~~~~~ ::

    sage: def all_sylow(G, p):
    ....:     '''Form the set of all distinct Sylow p-subgroups of G'''
    ....:     scriptP = []
    ....:     P = G.sylow_subgroup(p)
    ....:     for x in G:
    ....:         H = P.conjugate(x)
    ....:         if not(H in scriptP):
    ....:             scriptP.append(H)
    ....:     return scriptP

~~~~~~~~~~~~~~~~~~~~~~ ::

    sage: G = DihedralGroup(18)
    sage: S2 = G.sylow_subgroup(2); S2
    Subgroup generated by
    [(2,18)(3,17)(4,16)(5,15)(6,14)(7,13)(8,12)(9,11),
     (1,10)(2,11)(3,12)(4,13)(5,14)(6,15)(7,16)(8,17)(9,18)]
    of (Dihedral group of order 36 as a permutation group)

~~~~~~~~~~~~~~~~~~~~~~ ::

    sage: uniqS2 = all_sylow(G, 2)
    sage: uniqS2
    [Permutation Group with generators [(2,18)(3,17)(4,16)(5,15)(6,14)(7,13)(8,12)(9,11), (1,10)(2,11)(3,12)(4,13)(5,14)(6,15)(7,16)(8,17)(9,18)],
     Permutation Group with generators [(1,7)(2,6)(3,5)(8,18)(9,17)(10,16)(11,15)(12,14), (1,10)(2,11)(3,12)(4,13)(5,14)(6,15)(7,16)(8,17)(9,18)],
     Permutation Group with generators [(1,10)(2,11)(3,12)(4,13)(5,14)(6,15)(7,16)(8,17)(9,18), (1,13)(2,12)(3,11)(4,10)(5,9)(6,8)(14,18)(15,17)],
     Permutation Group with generators [(1,10)(2,11)(3,12)(4,13)(5,14)(6,15)(7,16)(8,17)(9,18), (1,15)(2,14)(3,13)(4,12)(5,11)(6,10)(7,9)(16,18)],
     Permutation Group with generators [(1,3)(4,18)(5,17)(6,16)(7,15)(8,14)(9,13)(10,12), (1,10)(2,11)(3,12)(4,13)(5,14)(6,15)(7,16)(8,17)(9,18)],
     Permutation Group with generators [(1,9)(2,8)(3,7)(4,6)(10,18)(11,17)(12,16)(13,15), (1,10)(2,11)(3,12)(4,13)(5,14)(6,15)(7,16)(8,17)(9,18)],
     Permutation Group with generators [(1,10)(2,11)(3,12)(4,13)(5,14)(6,15)(7,16)(8,17)(9,18), (1,11)(2,10)(3,9)(4,8)(5,7)(12,18)(13,17)(14,16)],
     Permutation Group with generators [(1,10)(2,11)(3,12)(4,13)(5,14)(6,15)(7,16)(8,17)(9,18), (1,17)(2,16)(3,15)(4,14)(5,13)(6,12)(7,11)(8,10)],
     Permutation Group with generators [(1,5)(2,4)(6,18)(7,17)(8,16)(9,15)(10,14)(11,13), (1,10)(2,11)(3,12)(4,13)(5,14)(6,15)(7,16)(8,17)(9,18)]]

~~~~~~~~~~~~~~~~~~~~~~ ::

    sage: len(uniqS2)
    9

~~~~~~~~~~~~~~~~~~~~~~ ::

    sage: G = DihedralGroup(18)
    sage: S3 = G.sylow_subgroup(3); S3
    Subgroup generated by
    [(1,7,13)(2,8,14)(3,9,15)(4,10,16)(5,11,17)(6,12,18),
     (1,15,11,7,3,17,13,9,5)(2,16,12,8,4,18,14,10,6)]
    of (Dihedral group of order 36 as a permutation group)

~~~~~~~~~~~~~~~~~~~~~~ ::

    sage: uniqS3 = all_sylow(G, 3)
    sage: uniqS3
    [Permutation Group with generators
    [(1,7,13)(2,8,14)(3,9,15)(4,10,16)(5,11,17)(6,12,18),
    (1,15,11,7,3,17,13,9,5)(2,16,12,8,4,18,14,10,6)]]

~~~~~~~~~~~~~~~~~~~~~~ ::

    sage: len(uniqS3)
    1

~~~~~~~~~~~~~~~~~~~~~~ ::

    sage: S3.is_normal(G)
    True

~~~~~~~~~~~~~~~~~~~~~~ ::

    sage: S3.is_cyclic()
    True

~~~~~~~~~~~~~~~~~~~~~~ ::

    sage: G = DihedralGroup(18)
    sage: S2 = G.sylow_subgroup(2)
    sage: S3 = G.sylow_subgroup(3)
    sage: N2 = G.normalizer(S2); N2
    Subgroup generated by
    [(2,18)(3,17)(4,16)(5,15)(6,14)(7,13)(8,12)(9,11),
     (1,10)(2,11)(3,12)(4,13)(5,14)(6,15)(7,16)(8,17)(9,18)]
    of (Dihedral group of order 36 as a permutation group)

~~~~~~~~~~~~~~~~~~~~~~ ::

    sage: N2 == S2
    True

~~~~~~~~~~~~~~~~~~~~~~ ::

    sage: N3 = G.normalizer(S3); N3
    Subgroup generated by [(2,18)(3,17)(4,16)(5,15)(6,14)(7,13)(8,12)(9,11),
    (1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18),
    (1,7,13)(2,8,14)(3,9,15)(4,10,16)(5,11,17)(6,12,18),
    (1,15,11,7,3,17,13,9,5)(2,16,12,8,4,18,14,10,6)] of (Dihedral group of
    order 36 as a permutation group)

~~~~~~~~~~~~~~~~~~~~~~ ::

    sage: N3 == G
    True

~~~~~~~~~~~~~~~~~~~~~~ ::

    sage: G = DihedralGroup(18)
    sage: a = G("(1,7,13)(2,8,14)(3,9,15)(4,10,16)(5,11,17)(6,12,18)")
    sage: b = G("(1,5)(2,4)(6,18)(7,17)(8,16)(9,15)(10,14)(11,13)")
    sage: H = G.subgroup([a, b])
    sage: H.order()
    6

~~~~~~~~~~~~~~~~~~~~~~ ::

    sage: N = G.normalizer(H)
    sage: N
    Subgroup generated by
    [(1,2)(3,18)(4,17)(5,16)(6,15)(7,14)(8,13)(9,12)(10,11),
    (1,5)(2,4)(6,18)(7,17)(8,16)(9,15)(10,14)(11,13),
    (1,7,13)(2,8,14)(3,9,15)(4,10,16)(5,11,17)(6,12,18)] of (Dihedral group of
    order 36 as a permutation group)

~~~~~~~~~~~~~~~~~~~~~~ ::

    sage: N.order()
    12

~~~~~~~~~~~~~~~~~~~~~~ ::

    sage: H.is_normal(G)
    False

~~~~~~~~~~~~~~~~~~~~~~ ::

    sage: H.is_normal(N)
    True

~~~~~~~~~~~~~~~~~~~~~~ ::

    sage: DC=DiCyclicGroup(16)
    sage: DC.order()
    64

~~~~~~~~~~~~~~~~~~~~~~ ::

    sage: DC.is_simple()
    False

~~~~~~~~~~~~~~~~~~~~~~ ::

    sage: ns = DC.normal_subgroups()
    sage: len(ns)
    9

~~~~~~~~~~~~~~~~~~~~~~ ::

    sage: G = SymmetricGroup(100)
    sage: a = G([(1,60),  (2,72),  (3,81),  (4,43),  (5,11),  (6,87),
    ....:         (7,34),  (9,63),  (12,46), (13,28), (14,71), (15,42),
    ....:         (16,97), (18,57), (19,52), (21,32), (23,47), (24,54),
    ....:         (25,83), (26,78), (29,89), (30,39), (33,61), (35,56),
    ....:         (37,67), (44,76), (45,88), (48,59), (49,86), (50,74),
    ....:         (51,66), (53,99), (55,75), (62,73), (65,79), (68,82),
    ....:         (77,92), (84,90), (85,98), (94,100)])
    sage: b = G([(1,86,13,10,47),  (2,53,30,8,38),
    ....:         (3,40,48,25,17),  (4,29,92,88,43),   (5,98,66,54, 65),
    ....:         (6,27,51,73,24),  (7,83,16,20,28),   (9,23,89,95,61),
    ....:         (11,42,46,91,32), (12,14, 81,55,68), (15,90,31,56,37),
    ....:         (18,69,45,84,76), (19,59,79,35,93),  (21,22,64,39,100),
    ....:         (26,58,96,85,77), (33,52,94,75,44),  (34,62,87,78,50),
    ....:         (36,82,60,74,72), (41,80,70,49,67),  (57,63,71,99,97)])
    sage: a.order(), b.order()
    (2, 5)

~~~~~~~~~~~~~~~~~~~~~~ ::

    sage: HS = G.subgroup([a, b])
    sage: HS.order()
    44352000

~~~~~~~~~~~~~~~~~~~~~~ ::

    sage: HS.is_simple()
    True

~~~~~~~~~~~~~~~~~~~~~~ ::

    sage: gap.version()  # random
    '4.10.0'

~~~~~~~~~~~~~~~~~~~~~~ ::

    sage: G = gap('Group( (1,2,3,4,5,6), (1,3,5) )')
    sage: G
    Group( [ (1,2,3,4,5,6), (1,3,5) ] )

~~~~~~~~~~~~~~~~~~~~~~ ::

    sage: G.Center()
    Group( [ (1,3,5)(2,4,6) ] )

~~~~~~~~~~~~~~~~~~~~~~ ::

    sage: G.Centralizer('(1, 3, 5)')
    Group( [ (1,3,5), (2,4,6), (1,3,5)(2,4,6) ] )

~~~~~~~~~~~~~~~~~~~~~~ ::

    sage: print(gap.help('SymmetricGroup', pager=False))   # not tested

"""
