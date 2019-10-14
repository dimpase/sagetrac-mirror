r"""
Poisson vertex algebra
AUTHORS

- Reimundo Heluani (08-09-2019): Initial implementation
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


from sage.structure.parent import Parent
from sage.structure.unique_representation import UniqueRepresentation
from sage.structure.element_wrapper import ElementWrapper
from sage.misc.cachefunc import cached_method 
from sage.categories.vertex_algebras import VertexAlgebras
from sage.categories.poisson_vertex_algebras import PoissonVertexAlgebras
from vertex_algebra import UniversalEnvelopingVertexAlgebra
from vertex_algebra_quotient import VertexAlgebraQuotient
from sage.combinat.partition import Partition
from sage.sets.family import Family

class PoissonVertexAlgebra(Parent, UniqueRepresentation):
    @staticmethod
    def __classcall_private__(cls, R=None, arg0=None, **kwds):
        if R is None: 
            raise ValueError("First argument must be a ring!")
       
        try: 
            if R.has_coerce_map_from(arg0.base_ring()) and \
                arg0 in VertexAlgebras(arg0.base_ring()):
                if isinstance(arg0, UniversalEnvelopingVertexAlgebra):
                    return PoissonVertexAlgebra_from_chiral_envelope(R, arg0, **kwds)
                if isinstance(arg0, VertexAlgebraQuotient):
                    return PoissonVertexAlgebra_from_quotient(R, arg0, **kwds)
        except AttributeError: 
            pass

        print "Nothing to construct"

    def __init__(self, R, **kwds):
        category = kwds.get('category', None)
        category = PoissonVertexAlgebras(R).or_subcategory(category)
        super(PoissonVertexAlgebra, self).__init__(base=R, names = 
            kwds.get('names', None), category = category)

class PVA_from_vertex_algebra_element(ElementWrapper):

    def _lmul_(self,scalar):
        return self._acted_upon_(scalar)

    def is_monomial(self):
        return ( len(self.monomial_coefficients()) == 1  or self.is_zero() )


class PoissonVertexAlgebra_from_vertex_algebra(PoissonVertexAlgebra):

    def __init__(self, R, V, **kwds):
        if V not in VertexAlgebras(R).FinitelyGenerated():
            raise ValueError ("V needs to be a finitely generated " \
                "vertex algebra, got {}".format(V) )

        category=kwds.get('category', None)
        category = PoissonVertexAlgebras(R).or_subcategory(category)
        if V in VertexAlgebras(R).HGraded():
            category = category.HGraded()
        category = category.FinitelyGenerated()
        kwds['category'] = category
        
        try:
            vnames = V.variable_names()
        except:
            vnames = None

        kwds['names'] = kwds.get('names', vnames)
        

        super(PoissonVertexAlgebra_from_vertex_algebra, self).__init__(R, **kwds)
        self._va = V

    def _repr_(self):
        return "The Poisson vertex algebra quasi-classical limit of {}"\
                    .format(self._va)

    def _coerce_map_from_(self, V):
        if self._va.has_coerce_map_from(V):
            return True

    def gens(self):
        return self._va.gens()
    
    def gen(self,i):
        return self.gens()[i]

    Element = PVA_from_vertex_algebra_element

class PoissonVertexAlgebra_from_chiral_envelope(
                                    PoissonVertexAlgebra_from_vertex_algebra):

    def __init__(self, R, V, **kwds):
        if not isinstance(V,UniversalEnvelopingVertexAlgebra):
            raise ValueError ("V needs to be a chiral envelope, " \
                "got {}".format(V) )

        super(PoissonVertexAlgebra_from_chiral_envelope, self).__init__(R, V,
                                                                        **kwds)
        self._li_graded = kwds.get('li_graded', True)

    def _element_constructor_(self,x):
        #self=self._va as modules
        if x in self.base_ring():
            return self.one()._acted_upon_(x)

        if x in self._va:
            return self.element_class(self, self._va(x))

        return self.element_class(self, self._va(x))

    @cached_method
    def zero(self):
        return self.element_class(self, self._va.zero())

    @cached_method
    def one(self):
        return self.element_class(self, self._va.vacuum())


    def basis(self):
        return Family ( self._va.basis(), lambda i : self(i), lazy = True )

    class Element(PVA_from_vertex_algebra_element):
        def _repr_(self):
            return self.lift()._repr_()

        def lift(self):
            return self.value

        def _add_(self,right):
            return type(self)(self.parent(), self.value + right.value)

        def _sub_(self, right):
            return type(self)(self.parent(), self.value - right.value)

        def T(self,n=1):
            return self.parent()(self.value.T(n))

        def __nonzero__(self):
            return bool(self.value)

        def __getitem__(self, i):
            return self.value.__getitem__(i)

        def _acted_upon_(self, scalar, self_on_left=False):
            return type(self)(self.parent(), self.value._acted_upon_(scalar,
                                                        self_on_left))
        def monomial_coefficients(self):
            """
            Return the monomial coefficients of ``self`` as a dictionary.
           """
            c = self.value.monomial_coefficients()
            p = self.parent()
            return { p(k) : c[k] for k in c.keys() } 

        def _pbw_one_less(self):
            x,y,c = self.lift()._pbw_one_less()
            if x is None:
                return (None, None, None)
            p = self.parent()
            return (p(x),p(y),c)

        def PBW_filtration_degree(self):
            return self.lift().PBW_filtration_degree()
        
        def li_filtration_degree(self):
            return self.lift().li_filtration_degree()

        def _bracket_(self, other):
            #cheaper to compute directly
            p = self.parent()
            ret = {}
            for k in other.monomials():
                l,sf,c = k._pbw_one_less()
                if l == p.one():
                    continue
                if k.PBW_filtration_degree() == 1:
                    dk = k.li_filtration_degree()
                    for k2 in self.monomials():
                        l2,sf2,c2 = k2._pbw_one_less()
                        if l2 == p.one():
                            continue
                        if k2.PBW_filtration_degree() == 1:
                            dk2 = k2.li_filtration_degree()
                            br = k2.lift().bracket(k.lift())
                            for j in br.keys():
                                rec = ret.get(j,p.zero())
                                ret[j] = rec + sum( p(m) for m in br[j].monomials()
                                    if (not p._li_graded) or (
                                    m.li_filtration_degree() == dk + dk2 - j) )
                        else:
                            #skew-symmetry
                            br = k._bracket_(k2)
                            for l in range(max(br.keys())+1):
                                rec = ret.get(l, p.zero())
                                ret[l] = rec + sum( (-1)**(j+1)*br[j].T(j-l) 
                                            for j in br.keys() if j >= l )
                else:
                    #Leibniz identity
                    br = self._bracket_(l)
                    for j in br.keys():
                        rec = ret.get(j, p.zero())
                        ret[j] = rec + c*br[j]._mul_(sf)
                    br = self._bracket_(sf)
                    for j in br.keys():
                        rec = ret.get(j, p.zero())
                        ret[j] = rec + c*l._mul_(br[j])
            return { k:ret[k] for k in ret.keys() if ret[k] } 

        #TODO: this method relies in self.value.value directly
        def _mul_(self,right):
            p = self.parent()
            svmc = self.value.value.monomial_coefficients()
            rvmc = right.value.value.monomial_coefficients()
            return sum ( v1*v2*p(partmultiply(k1,k2)) for k1,v1 in 
                svmc.items() for k2,v2 in rvmc.items() )

        def weight(self):
            return self.lift().weight()

def partmultiply(p1,p2):
    ng = len(p1)
    ret = [[]]*(ng)
    for j in range(len(p1)):
        l1 = p1[j].to_exp()
        l2 = p2[j].to_exp()
        m = max(len(l1), len(l2))
        l1 = p1[j].to_exp(m)
        l2 = p2[j].to_exp(m)
        ret[j] = Partition(exp=[l1[i]+l2[i] for i in range(m)])
    return ret

class PoissonVertexAlgebra_from_quotient(
                PoissonVertexAlgebra_from_vertex_algebra):

    def __init__(self, R, V, **kwds):
        if not isinstance(V,VertexAlgebraQuotient):
            raise ValueError ("V needs to be a quotient of a chiral envelope, " \
                "got {}".format(V) )

        super(PoissonVertexAlgebra_from_quotient, self).__init__(R, V, **kwds)
        self._ambient = PoissonVertexAlgebra(self.base_ring(), V.ambient())

    def _element_constructor_(self,x):
        #self= the associated graded of self._va  as modules
        if x in self.base_ring():
            return self.one()._acted_upon_(x)

        if x in self._va:
            if x.is_zero():
                return self.zero()
            x = self._va(x)
            p = x.parent()
            sret = self.zero() 
            for k in x.monomials():
                w = k.weight()
                F = p.li_filtration(w)
                A = F[0].ambient()
                for j in F.keys():
                    try: 
                        ret = F[j].retract(A._from_dict(k.value[1].monomial_coefficients()))
                    except:
                        break
                Q = p.get_graded_part(w,j-1)
                sret += self.element_class(self, {w:{j-1:Q.retract(ret)}})
            return sret

        return self.element_class(self, x)

    @cached_method
    def zero(self):
        return self.element_class(self, {})

    @cached_method
    def one(self):
        return self(self._va.vacuum())


    class Element(PVA_from_vertex_algebra_element):
        def _repr_(self):
            return repr(self.value)

        def lift(self):
            Q = self.parent()._va
            V = Q.ambient()
            return sum ( Q.retract(V._from_dict(e.lift().lift()\
                .monomial_coefficients())) for m in self.monomials() for
                k,d in m.value.items() for l,e in d.items() )

        def _add_(self,other):
            def sumdict(d1,d2):
                ret = {}
                for k in d1.keys():
                    s = d1[k] + d2.get(k,0)
                    if not s.is_zero():
                        ret[k] = s
                for k in [k for k in d2.keys() if k not in d1.keys()]:
                    ret[k] = d2[k]
                return ret
            ret = {}
            for k in self.value.keys():
                s = sumdict(self.value[k], other.value.get(k,{}))
                if s:
                    ret[k] = s
            for k in [k for k in other.value.keys() if k not in self.value.keys()]:
                ret[k] = other.value[k]
            return type(self)(self.parent(),ret)

        def _sub_(self,other):
            def subdict(d1,d2):
                ret = {}
                for k in d1.keys():
                    s = d1[k] - d2.get(k,0) 
                    if not s.is_zero():
                        ret[k] = s
                for k in [k for k in d2.keys() if k not in d1.keys()]:
                    ret[k] = -d2[k]
                return ret
            ret = {}
            for k in self.value.keys():
                s = subdict(self.value[k], other.value.get(k,{}))
                if s:
                    ret[k] = s
            for k in [k for k in other.value.keys() if k not in self.value.keys()]:
                ret[k] = subdict({},other.value[k])
            return type(self)(self.parent(),ret)
                 
        def __nonzero__(self):
            return bool(self.value)

        def _acted_upon_(self,scalar, self_on_left=False):
            if scalar.is_zero():
                return self.parent().zero()
            return type(self)(self.parent(), {k: {l : scalar*m for l,m in 
                        self.value[k].items() } for k in self.value.keys() })

        def monomial_coefficients(self):
            ret = {}
            for k in self.value.keys():
                for j in self.value[k].keys():
                    Q = self.parent()._va.get_graded_part(k,j).basis()
                    for l,v in self.value[k][j].monomial_coefficients().items():
                        ret[(k,(j,Q[l]))] = v
            return ret

        def monomials(self):
            return [type(self)(self.parent(), {k[0]:{k[1][0]: v*k[1][1]}}) \
                    for k,v in self.monomial_coefficients().items()]

        def _bracket_(self,right):
            p = self.parent()
            ret = {}
            if self.is_zero() or right.is_zero():
                return ret
            for s in self.monomials():
                for r in right.monomials():
                    ks,ds = s._bidegree()
                    kr,dr = r._bidegree()
                    x=p._ambient(s.lift().lift())
                    y=p._ambient(r.lift().lift())
                    br = x._bracket_(y)
                    pbr = { k:p(p._va.retract(v.lift()))._get_bigraded_term(
                            ks+kr-k-1,ds+dr-k) for k,v in br.items() }
                    pbr = { k:v for k,v in pbr.items() if not p(v).is_zero()}
                    for k in pbr.keys():
                        old = ret.get(k,p.zero())
                        ret[k] = old + pbr[k]
            return ret

        def _mul_(self,right):
            p = self.parent()
            ret = p.zero()
            if self.is_zero() or right.is_zero():
                return ret
            for s in self.monomials():
                for r in right.monomials():
                    ks,ds = s._bidegree()
                    kr,dr = r._bidegree()
                    x=p._ambient(s.lift().lift())
                    y=p._ambient(r.lift().lift())
                    ret += p(p._va.retract((x._mul_(y)).lift()))\
                                ._get_bigraded_term(ks+kr,ds+dr)    
            return ret

        def weight(self):
            if len(self.value) != 1:
                raise ValueError("{} is not homogeneous".format(self))
            return self.value.keys()[0]

        def li_filtration_degree(self):
            ls = [ r[0] for k,l in self.value.items() for r in l.items()]
            if ls[1:] == ls[:-1]:
                return ls[0]
            raise ValueError("{} is not homogeneous".format(self))

        def _bidegree(self):
            if self.is_zero():
                return (0,0)
            if len(self.value) != 1:
                raise ValueError("{} is not a monomial".format(self))
            if len(self.value.items()[0][1]) != 1:
                raise ValueError("{} is not a monomial".format(self))
            return (self.value.items()[0][0],
                                        self.value.items()[0][1].items()[0][0])

        def _get_bigraded_term(self,m,n):
            v = self.value.get(m,{})
            v = v.get(n,self.parent().zero())
            if v.is_zero():
                return self.parent().zero()
            return type(self)(self.parent(), {m:{n:v}})
    
        def T(self,n=1):
            return self.parent()(self.lift().T(n))


        

