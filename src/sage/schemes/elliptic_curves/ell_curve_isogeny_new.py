from sage.categories import homset

from sage.categories.morphism import Morphism
from sage.rings.polynomial.polynomial_element import is_Polynomial
from sage.rings.polynomial.polynomial_ring_constructor import PolynomialRing
from sage.schemes.elliptic_curves.all import EllipticCurve
from sage.misc.cachefunc import cached_method

def kernel_polynomial_from_points(kernel_gens, check=False):
    """
    Construct the kernel polynomial of the group generated by the
    points ``kernel_gens`` of an elliptic curve.
    
    INPUT:
    
    - ``kernel_gens`` -  a list of points of an elliptic curve.

    - ``check`` - if ``True`` (default), check that all points in
      ``kernel_gens`` have finite order.
                
    OUTPUT:
    
    - let `G` be the group generated by all the points in
      ``kernel_gens``, the function returns the polynomial
    
    .. math::

        h(x) = \prod_{Q\in G \setminus\{\mathcal O\}} (x-x(Q)).
        
    EXAMPLES::

        sage: from sage.schemes.elliptic_curves.ell_curve_isogeny_new import kernel_polynomial_from_points
        sage: E = EllipticCurve(GF(7),[1,2,3,4,5])
        sage: kernel_polynomial_from_points([E(0)],False)
        1
        sage: kernel_polynomial_from_points(E.points()[2:4],False)
        x^8 + 2*x^7 + 2*x^6 + 3*x^5 + 4*x^4 + x^3 + x^2
        sage: kernel_polynomial_from_points(E.points(),False)
        x^8 + 2*x^7 + 2*x^6 + 3*x^5 + 4*x^4 + x^3 + x^2
        sage: kernel_polynomial_from_points([E.points()[2]],False)
        x^2

    """
    E = kernel_gens[0].codomain()
    K = E.base_field()
    # Mais ca sert a quoi, ca? De toutes façons plus loin tu calcules l'ordre des points.
    if check and not all(P.has_finite_order() for P in kernel_gens):
        raise ValueError, "The points in the kernel must be of finite order."
    
    # Compute the group generated by the "kernel_gens"
    # Useless compatations are done here : we only need the abscissae of the points.
    # Morever, there is maybe a better algo to do that.

    # Non, il n'y a pas de meilleur algo. Pour ce qui en est des
    # abscisses, c'est vrai, on pourrait gagner un facteur constant
    # (~2) avec des formules XZ (voir courbes de Montgomery dans mon
    # cours), mais un utilisateur qui appelle cette fct n'est pas à un
    # facteur 2 près.
    kernel_list = set([E(0)])
    for P in kernel_gens:
        points_to_add = set()
        for j in range(P.order()):
            for Q in kernel_list:
                points_to_add.add(j*P+Q)
        kernel_list = kernel_list.union(points_to_add)
    kernel_list.remove(E(0))
    
    # Compute the kernel polynomial
    R = PolynomialRing(K,'x')
    x = R.gen()
    polyn = R(1)
    for P in kernel_list:
        polyn *= x - P.xy()[0]
    return polyn

def change_elliptic_coef((a1, a2, a3, a4, a6), (u,r,s,t)):
    """
    Compute the a-invariants of the elliptic curve isomorphic to
    `(a_1, ..., a_6)` via the isomorphism

    .. math::

        x = u^2 x' + r
        y = u^3 y' + s u^2 x' + t
    
    INPUT:
    
    - ``(a1, a2, a3, a4, a6)`` - a-invariants of an elliptic curve E.

    - ``(u, r, s, t)`` - tuple describing the change of variables; `u`
      has to be invertible.
    
    OUTPUT:
    
    - The a-invariants of the elliptic curve E after the `urst` change
      of variables.
    
    EXAMPLES::
        
        sage: from sage.schemes.elliptic_curves.ell_curve_isogeny_new import change_elliptic_coef
        sage: change_elliptic_coef([1,2,3,4,5],[1,0,0,0])
        (1, 2, 3, 4, 5)
        sage: change_elliptic_coef([1,2,3,4,5],[1,0,0,5])
        (1, 2, 13, -1, -35)
        sage: change_elliptic_coef([1,2,3,4,5],[6,-1,2,5])
        (5/6, -7/36, 1/18, -13/648, -11/15552)
        sage: change_elliptic_coef([1,2,3,4,5],[1,0,3,5])
        (7, -10, 13, -40, -35)

    TESTS::

        sage: x, y, u, r, s, t = SR.var('x, y, u, r, s, t')
        sage: ainvs = SR.var('a1, a2, a3, a4, a6')
        sage: e = SR(EllipticCurve([a1, a2, a3, a4, a6]))
        sage: e1 = e(x = u^2*x + r, y = u^3*y + s*u^2*x + t)/u^6
        sage: e2 = SR(EllipticCurve(change_elliptic_coef(ainvs, (u, r, s, t))))
        sage: bool(e1 - e2)
        True
    """ 
    try:
        iu = 1/u
    except ZeroDivisionError:
        raise ZeroDivisionError('u coefficient must be invertible.')
    a6 += r*(a4 + r*(a2 + r)) - t*(a3 + r*a1 + t)
    a4 += -s*a3 + 2*r*a2 - (t + r*s)*a1 + 3*r**2 - 2*s*t
    a3 += r*a1 + 2*t
    a2 += -s*a1 + 3*r - s**2
    a1 += 2*s
    return (a1*iu, a2*iu**2, a3*iu**3, a4*iu**4, a6*iu**6)

class EllipticIsogeny(Morphism):
    r"""
    Construct an elliptic curve isogeny.
    
    This class implements cyclic, separable isogenies of
    elliptic curves.

    .. WARNING::
        
        Characteristic 2 is not supported.
    
    INPUT:
    
    - ``E`` - An elliptic curve, the domain of the isogeny to
      initialize.

    - ``kernel`` - (default: ``None``) The kernel of the isogeny. Can
      be given as

        -  a point of ``E``,
        -  a list of points of ``E``,

      in which case the kernel of the isogeny is the group generated
      by the point(s). All points must have finite order. 

      Other options are

        - The *kernel polynomial*: a factor of the `m`-division
          polynomial, where `m` is the degree of the isogeny. It is a
          polynomial vanishing on the abscissas of the kernel with
          multiplicity equal to the inseparable degree .

        - A pair `(a, b)` of polynomials such that `a` divides `x^3 +
          a_2x^2 + a_4x + a_6` and `ab` defines the *kernel polynomial*.
          
        - The multiple of the *kernel polynomial* of the form `ab^2`, with
          `a` dividing `x^3 + a_2x^2 + a_4x + a_6`. In this case
          ``degree`` must be given. (NdL: Comme on disait: bof!)

    - ``codomain`` - (default:``None``) An elliptic curve, the
      codomain of the isogeny.

        - If ``kernel`` is ``None``, then this must be the codomain of
          a cyclic, separable, normalized isogeny, furthermore,
          ``degree`` must be the degree of the isogeny from ``E`` to
          ``codomain`` (not yet implemented).

        - If ``kernel`` is not ``None``, then this must be isomorphic
          to the codomain of the cyclic normalized separable isogeny
          defined by ``kernel``, in this case, the isogeny is post
          composed with an isomorphism so that the codomain coincides
          with ``codomain``.

    - ``degree`` - (default: ``None``) an integer: the degree of the
      isogeny.
      
      If ``kernel`` is ``None``, then this is the degree of the
      isogeny from ``E`` to ``codomain``.  If ``kernel`` is not
      ``None``, this is only needed when ``kernel`` is a multiple of
      the kernel polynomial.

    - ``urst`` - (default: ``None``) a 4-uple.  If not ``None``, the
      isogeny is post composed with the isomorphism defined by 
      `(u, r, s, t)`. See :py:func:`change_elliptic_coef`.

    - ``check`` - (default: ``True``) checks if ``kernel`` defines a
      valid isogeny.
    
    EXAMPLES::
    
        sage: from sage.schemes.elliptic_curves.ell_curve_isogeny_new import EllipticIsogeny
        sage: F = GF(19)
        sage: R.<x> = PolynomialRing(F)
        sage: E=EllipticCurve(F,[1,2,3,4,5])
        
    We can define the isogeny from a kernel polynomial::
    
        sage: phi = EllipticIsogeny(E,x+9); phi
        Isogeny of degree 3:
          From: Elliptic Curve defined by y^2 + x*y + 3*y = x^3 + 2*x^2 + 4*x + 5 over Finite Field of size 19
          To:   Elliptic Curve defined by y^2 + x*y + 3*y = x^3 + 2*x^2 + 14*x + 11 over Finite Field of size 19
          Defn: (x,y) |--> ((x^2 + 9*x - 2)/(x + 9), (x^2*y - x*y + 2*x + 7*y - 7)/(x^2 - x + 5))

        sage: phi2 = EllipticIsogeny(E,x+9, urst = (2,3,5,7)); phi2
        Isogeny of degree 3:
          From: Elliptic Curve defined by y^2 + x*y + 3*y = x^3 + 2*x^2 + 4*x + 5 over Finite Field of size 19
          To:   Elliptic Curve defined by y^2 + 15*x*y + 12*y = x^3 + 18*x + 1 over Finite Field of size 19
          Defn: (x,y) |--> ((4*x^2 + x)/(x + 9), (x^3 + 8*x^2*y + 6*x^2 - 8*x*y - 7*x - y - 1)/(x^2 - x + 5))
    
    We can also define it from a list of generators of the kernel::       
          
        sage: E = EllipticCurve(GF(7), [0,0,0,1,0])
        sage: phi = EllipticIsogeny( E, E((0,0)) ); phi
        Isogeny of degree 2:
          From: Elliptic Curve defined by y^2 = x^3 + x over Finite Field of size 7
          To:   Elliptic Curve defined by y^2 = x^3 + 3*x over Finite Field of size 7
          Defn: (x,y) |--> ((x^2 + 1)/x, (x^2*y - y)/x^2)

    ALGORITHM:

    Citer Velu.
    
    See [DeF]_, section 8.2 for complete presentation and justification of the following
    formulas.
    
    Let `\phi : E \to E'` be an isogeny of degree `\ell` between two elliptic curves
    and `h` be the *kernel polynomial* of `\phi`, i.e.
    
    .. math::

        h(x) = \prod_{Q\in \ker \phi \setminus\{\mathcal O\}} (x-x(Q)).
    
    Denote by `s_i` the `i`-th  power sum of the roots of `h`.
    
    The simplest case occurs when the equation of `E` is of the form `y^2=f(x)`, with 
    `f(x) = x^3 + a_2 x^2 + a_4 x + a_6`. In this case, one can easily compute the
    fractions defining the isogeny:
    
    .. math::
    
        \phi(x,y) = \left( \frac{g(x)}{h(x)}, y \left(\frac{g(x)}{h(x)}\right)'\right),
    
    where
    
    .. math::
        
        \frac{g(x)}{h(x)} = \ell x - s_1 - f'(x) \frac{h'(x)}{h(x)} - 2 f(x) \left(\frac{h'(x)}{h(x)} \right)'.
    
    Moreover, the equation of `E'` is given by:
    
    .. math::

        E':\quad y^2 = x^3 + a_2 x^2 +(a_4-5t)x + a_6 - a_2t - 7w,
        
    where:
    
    .. math::
    
        t = 3s_2 + 2 a_2 s_1 + (\ell-1)a_4,\quad  w = 5 s_3 + 4 a_2 s_2 + 3 a_4 s_1 +2 (\ell-1) a_6.
        
    When the equation of `E` is of the form `y^2+ a_1 x y + a_3 y = x^3 + a_2 x^2 + a_4 x + a_6`
    with `a_1 \neq 0` or `a_3 \neq 0`, the class internally proceed to the following 
    change of variables:
    
    .. math::
    
        \alpha: y \mapsto y - \frac{a_1}2 x - \frac{a_3}2,
        
    hence, we have an isomorphism to a new curve `E_1` whose equation
    is of the form above. Note that abscissas are not modified, so the
    kernel polynomial is the same. Then we can compute the codomain
    `E_2` and the rational maps of the isogeny `\psi : E_1 \to E_2`
    via the formulas above. Finally, we apply the change of variables
    `\alpha^{-1}` (NdL: pas tres correct ça) to `E_2`. 

    This convention guarantees that ``phi = EllipticIsogeny(E, E(0))``
    is the trivial automorphism.
    
    The construction is summarized by the following commutative
    diagram:
    
    .. math::
    
        \begin{matrix} &    &  \scriptsize  \phi   &  &\\
                       &E  & \longrightarrow & E' & \\
               \scriptsize \alpha &\downarrow & &\uparrow & \scriptsize\alpha^{-1} \\
                       & E_1 &  \longrightarrow & E_2 & \\
                       &     &   \scriptsize\psi           &     & \\
        \end{matrix}
    
    REFERENCES:
    
    .. [DeF] De Feo, "Fast algorithms for towers of finite fields and isogenies".
    """
    def __init__(self, E, kernel=None, codomain=None, degree=None, urst=None, check=True):
        """
        TESTS::
        
            sage: from sage.schemes.elliptic_curves.ell_curve_isogeny_new import EllipticIsogeny
            sage: E = EllipticCurve(GF(31), [0,0,0,1,0])
            sage: P = E((2,17))
            sage: phi = EllipticIsogeny(E, P); phi
            Isogeny of degree 8:
              From: Elliptic Curve defined by y^2 = x^3 + x over Finite Field of size 31
              To:   Elliptic Curve defined by y^2 = x^3 + 10*x + 28 over Finite Field of size 31
              Defn: (x,y) |--> ((x^8 - 7*x^7 - 12*x^6 + 10*x^5 - 13*x^4 + 10*x^3 - 12*x^2 - 7*x + 1)/(x^7 - 7*x^6 - 4*x^5 - 11*x^4 - 4*x^3 - 7*x^2 + x), (x^11*y + 5*x^10*y + x^9*y + 10*x^8*y - 14*x^7*y - 2*x^6*y - 2*x^5*y - 14*x^4*y + 10*x^3*y + x^2*y + 5*x*y + y)/(x^11 + 5*x^10 - 7*x^9 - 7*x^8 + 12*x^7 - 12*x^6 + 7*x^5 + 7*x^4 - 5*x^3 - x^2))

            sage: E = EllipticCurve('17a1')
            sage: R.<x> = PolynomialRing(QQ,'x')
            sage: phi = EllipticIsogeny(E, 41/3 -55*x -x**2 -x**3 + x**4); phi
            Isogeny of degree 9:
              From: Elliptic Curve defined by y^2 + x*y + y = x^3 - x^2 - x - 14 over Rational Field
              To:   Elliptic Curve defined by y^2 + x*y + y = x^3 - x^2 - 56*x - 10124 over Rational Field
              Defn: (x,y) |--> ((x^9 - 2*x^8 + 10*x^7 + 1319*x^6 - 2004*x^5 + 3103/3*x^4 + 27341/3*x^3 - 19588/3*x^2 - 33703/3*x - 1521032/9)/(x^8 - 2*x^7 - x^6 - 108*x^5 + 415/3*x^4 + 248/3*x^3 + 8993/3*x^2 - 4510/3*x + 1681/9), (1/9*x^12*y - 1/3*x^11*y - 11/9*x^11 - 11/9*x^10*y - 2146/9*x^10 - 3025/9*x^9*y + 10664/27*x^9 + 2255/3*x^8*y - 3248/9*x^8 - 3916/3*x^7*y - 140111/9*x^7 - 330719/9*x^6*y + 27172/9*x^6 + 168445/3*x^5*y + 214009/9*x^5 - 189080/9*x^4*y + 1936994/27*x^4 + 838090/9*x^3*y - 506180/27*x^3 - 74896*x^2*y - 4451336/27*x^2 - 1472371/9*x*y - 43990709/27*x - 18743927/9*y - 221896319/243)/(1/9*x^12 - 1/3*x^11 - 160/9*x^9 + 371/9*x^8 + 80/9*x^7 + 967*x^6 - 4556/3*x^5 - 11891/27*x^4 - 487276/27*x^3 + 370394/27*x^2 - 92455/27*x + 68921/243))
        """
        R = PolynomialRing(E.base_ring().fraction_field(), 'x')
        x = R.gen()
        f = x**3 + E.a2()*x**2 + E.a4()*x + E.a6()

        if isinstance(kernel, (tuple, list)) and is_Polynomial(kernel[0]) :
            a, b = kernel
            self.h = R(a)*R(b)**2
        elif is_Polynomial(kernel):
            if degree == None:
                a = R(kernel).gcd(f)
                b, _ = R(kernel).quo_rem(a)
                self.h = a*b**2
            else:
                if degree == kernel.degree()+1:
                    self.h = R(kernel)
                else:
                    a = R(kernel).gcd(f)
                    b, _ = R(kernel).quo_rem(a)
                    self.h = a*b**2
        elif isinstance(kernel,(list,tuple)) and kernel[0] in E:
            self.h = kernel_polynomial_from_points(kernel, check)
        elif kernel in E:
            self.h = kernel_polynomial_from_points([kernel], check)
        else:
            raise ValueError, "The parameter kernel must be a polynomial, a nonempty list of points of E or a point of E."
            
        self._init_via_kernel_polynomial(E, codomain, urst)
        
    def _init_via_kernel_polynomial(self, E, codomain, urst):
        """
        Initialize the isogeny, assuming that the kernel polynomial of
        the isogeny is in ``self.h``.
        
        INPUT:
        
        - ``E`` - the domain of the isogeny (an elliptic curve).
        - ``codomain`` - same as ``codomain`` in the constructor of the class. 
        - ``urst`` - same as ``urst`` in the constructor of the class. 
        
        EXAMPLES::
        
            sage: from sage.schemes.elliptic_curves.ell_curve_isogeny_new import EllipticIsogeny
            sage: E = EllipticCurve(GF(31), [0,0,0,1,0])
            sage: P = E((2,17))
            sage: phi = EllipticIsogeny(E, P); phi      # indirect doctest
            Isogeny of degree 8:
              From: Elliptic Curve defined by y^2 = x^3 + x over Finite Field of size 31
              To:   Elliptic Curve defined by y^2 = x^3 + 10*x + 28 over Finite Field of size 31
              Defn: (x,y) |--> ((x^8 - 7*x^7 - 12*x^6 + 10*x^5 - 13*x^4 + 10*x^3 - 12*x^2 - 7*x + 1)/(x^7 - 7*x^6 - 4*x^5 - 11*x^4 - 4*x^3 - 7*x^2 + x), (x^11*y + 5*x^10*y + x^9*y + 10*x^8*y - 14*x^7*y - 2*x^6*y - 2*x^5*y - 14*x^4*y + 10*x^3*y + x^2*y + 5*x*y + y)/(x^11 + 5*x^10 - 7*x^9 - 7*x^8 + 12*x^7 - 12*x^6 + 7*x^5 + 7*x^4 - 5*x^3 - x^2))       
        """
        a1, a2, a3, a4, a6 = E.ainvs()
        self._pre_urst = (1, 0, 0, 0)
        self._domain_reduced = E
        if a1 != 0 or a3 != 0:
            if E.base_ring().characteristic() == 2:
                raise NotImplementedError, "The characteristic 2 is not supported"
            self._pre_urst = (1, 0, a1/2, a3/2)
            # Pourquoi ne pas utiliser change_elliptic_coef?
            a1, a3 = E.base_field()(0), E.base_field()(0)
            a2, a4, a6 = E.b2()/4, E.b4()/2, E.b6()/4
            self._domain_reduced = EllipticCurve((a1,a2,a3,a4,a6))
        # Compute power sums of roots of h
        n = self.h.degree()
        c1, c2, c3 = (self.h[n-i] for i in range(1,4))
        s1 = -c1
        s2 = c1**2 - 2*c2
        s3 = -c1**3 + 3*c1*c2 - 3*c3
        # End of power sum computing
        
        # Apply Velu's formulas
        t = 3*s2 + 2*a2*s1 + n*a4
        w = 5*s3 + 4*a2*s2 + 3*a4*s1 +2*n*a6
        
        a4 = a4 - 5*t
        a6 = a6 - 4*a2*t - 7*w
        # End of Velu's formulas
        
        (a1, a2, a3, a4, a6) = change_elliptic_coef((a1, a2, a3, a4, a6), self._pre_urst)
        E2 = None
        if codomain is not None:
            E2 = EllipticCurve((a1, a2, a3, a4, a6))
            urst = isomorphisms(E2, codomain, JustOne = True)
            if urst is None:
                raise ValueError, "Codomain parameter must be isomorphic to computed codomain isogeny"
            self.urst = urst
            E2 = codomain
        elif urst is not None:
            self.urst  = urst
            E2 = EllipticCurve(change_elliptic_coef((a1, a2, a3, a4, a6), urst))
        else:
            E2 = EllipticCurve((a1, a2, a3, a4, a6))
            self.urst  = (1, 0, 0, 0)
        # Multiply urst by the unit of the base_field in order to coerce urst properly
        unit = E2.base_ring().fraction_field()(1)
        self.urst = u, r, s, t = tuple( i*unit for i in self.urst)
        self.urst_inv = (1/u, -r/(u**2), -s/u, (r*s - t)/(u**3))
        parent = homset.Hom(E,E2)
        Morphism.__init__(self, parent)

        
      
    def _call_(self, P):
        """
        Evaluate `\phi(P)`.
        
        INPUT:
        
        - P - A point of ``self.domain()``.
        
        EXAMPLES::
        
            sage: from sage.schemes.elliptic_curves.ell_curve_isogeny_new import EllipticIsogeny
            sage: E = EllipticCurve(GF(17), [1, 9, 5, 4, 3])
            sage: R.<x> = PolynomialRing(GF(17),'x')
            sage: phi = EllipticIsogeny(E, 6+13*x+x**2)
            sage: phi(E((1,0)))
            (15 : 13 : 1)
            
            sage: E = EllipticCurve(GF(23^2,'a'), [0,0,0,1,0])
            sage: phi = EllipticIsogeny(E, E((0,0)))
            sage: phi(E((1,5)))
            (2 : 0 : 1)
            sage: phi(E(15,20))
            (12 : 1 : 1)

            sage: E = EllipticCurve(QQ, [0,0,0,3,0])
            sage: P = E((1,2))
            sage: R.<x> = PolynomialRing(QQ,'x')
            sage: phi = EllipticIsogeny(E, x)
            sage: phi(P)
            (4 : -4 : 1)
            sage: phi(-P)
            (4 : 4 : 1)
        """
        E, E2 = self.domain(), self.codomain()
        
        P = E(P)
        if P.is_zero() or self.h(P.xy()[0]) == 0 :
            return E2(0)

        x, y = P.xy()            
        _,_,s,t = self._pre_urst
        y += s*x + t
        x_map, y_map = self._internal_maps()
        xn = x_map(x)
        yn = y*y_map(x) - s*xn -t
        
        u,r,s,t= self.urst_inv
        return E2( (u**2*xn + r, u**3*yn + s*u**2*xn + t) )
    
    @cached_method        
    def _internal_maps(self):
        r"""
        Compute the fractions `\frac{g(x)}{h(x)}` and `\left(\frac{g(x)}{h(x)}\right)'`
        (see :py:class:`EllipticIsogeny`).
        
        This method is used by :py:meth:`rational_maps` and :py:meth:`_call_`.
        
        EXAMPLES::
        
            sage: from sage.schemes.elliptic_curves.ell_curve_isogeny_new import EllipticIsogeny
            sage: E = EllipticCurve(GF(23^2,'a'), [0,0,0,1,0])
            sage: phi = EllipticIsogeny(E, E((0,0)))
            sage: phi._internal_maps()
            ((x^2 + 1)/x, (x^2 + 22)/x^2)
        
        """
        n = self.h.degree()
        x = self.h.parent().gen()
        s1 = -self.h.list()[n-1] if self.h.degree()> 0 else 0
        E = self._domain_reduced
        f = x**3 + E.a2()*x**2 + E.a4()*x + E.a6()
        fp = f.derivative()
        hp_o_h = self.h.derivative() / self.h

        x_map = (n+1)*x - s1 - fp*hp_o_h - 2*f*(hp_o_h.derivative())
        y_map = x_map.derivative()

        return x_map, y_map
        
    @cached_method
    def rational_maps(self):
        r"""
        Return this isogeny as a pair of rational maps.

        EXAMPLES::

            sage: from sage.schemes.elliptic_curves.ell_curve_isogeny_new import EllipticIsogeny
            sage: E = EllipticCurve(QQ, [0,2,0,1,-1])
            sage: R.<x> = PolynomialRing(QQ)
            sage: phi = EllipticIsogeny(E, R(1))
            sage: phi.rational_maps()
            (x, y)

            sage: E = EllipticCurve(GF(17), [0,0,0,3,0])
            sage: phi = EllipticIsogeny(E,  E((0,0)))
            sage: phi.rational_maps()
            ((x^2 + 3)/x, (x^2*y - 3*y)/x^2)
        """
        R = PolynomialRing(self.domain().base_ring().fraction_field(), 2, 'xy').fraction_field()
        x, y = R.gens()
        
        _,_,s,t = self._pre_urst
        x_map, y_map = self._internal_maps()
        phi_x, phi_y = x_map, y*y_map - s*x_map - t
        phi_y = phi_y(y=y+s*x+t)

        u, r, s, t = self.urst        
        phi_x, phi_y = R(u**2*phi_x + r), R(u**3*phi_y + s*u**2*phi_x + t)
        return phi_x, phi_y

    def degree(self):
        """
        Return the degree of this isogeny.

        EXAMPLES::

            sage: from sage.schemes.elliptic_curves.ell_curve_isogeny_new import EllipticIsogeny
            sage: E = EllipticCurve(QQ, [0,0,0,1,0])
            sage: phi = EllipticIsogeny(E,  E((0,0)))
            sage: phi.degree()
            2
            sage: R.<x> = PolynomialRing(QQ)
            sage: phi = EllipticIsogeny(E, x+x**3)
            sage: phi.degree()
            4
            sage: R.<x> = PolynomialRing(GF(31))
            sage: E = EllipticCurve(GF(31), [1,0,0,1,2])
            sage: phi = EllipticIsogeny(E, 17+x)
            sage: phi.degree()
            3
        """
        return self.h.degree() + 1
        
    def is_normalized(self):
        r"""
        Returns ``True`` if this isogeny is normalized. 

        An isogeny `\phi\colon E\to E_2` between two Weierstrass
        curves is said to be normalized if the `\phi*(\omega_2) =
        \omega`, where `\omega` and `omega_2` are the invariant
        differentials of `E` and `E_2` respectively.
        
        EXAMPLES::
        
            sage: from sage.schemes.elliptic_curves.ell_curve_isogeny_new import EllipticIsogeny
            sage: E = EllipticCurve(GF(7), [0,0,0,1,0])
            sage: R.<x> = GF(7)[]
            sage: phi = EllipticIsogeny(E, x)
            sage: phi.is_normalized()
            True
            sage: phi2 = EllipticIsogeny(E,x,urst=(3, 0, 0, 0))
            sage: phi2.is_normalized()
            False
        """
        return self.urst[0] == 1
    
    def _repr_defn(self):
        r"""
        Return a string describing the rational_maps of self.
        
        EXAMPLES::
        
            sage: from sage.schemes.elliptic_curves.ell_curve_isogeny_new import EllipticIsogeny
            sage: E = EllipticCurve(GF(7), [0,0,0,1,0])
            sage: R.<x> = GF(7)[]
            sage: phi = EllipticIsogeny(E, x)
            sage: phi._repr_defn()
            '(x,y) |--> ((x^2 + 1)/x, (x^2*y - y)/x^2)'
        """
        return '(x,y) |--> ' + str(self.rational_maps())
    
    def _repr_(self):
        r"""
        Return a string describing self.

        EXAMPLES::
            
            sage: from sage.schemes.elliptic_curves.ell_curve_isogeny_new import EllipticIsogeny
            sage: E = EllipticCurve(GF(7), [0,0,0,1,0])
            sage: R.<x> = GF(7)[]
            sage: phi = EllipticIsogeny(E, x); phi._repr_()
            'Isogeny of degree 2:\n  From: Elliptic Curve defined by y^2 = x^3 + x over Finite Field of size 7\n  To:   Elliptic Curve defined by y^2 = x^3 + 3*x over Finite Field of size 7\n  Defn: (x,y) |--> ((x^2 + 1)/x, (x^2*y - y)/x^2)'
        """
        D = self.domain()
        if D is None:
            return "Defunct map"
        s = "Isogeny of degree %d:" % self.degree()
        s += "\n  From: %s" % D
        s += "\n  To:   %s" % self.codomain()
        s += "\n  Defn: %s" % ('\n        '.join(self._repr_defn().split('\n')))
        return s
        
def isomorphisms(E,F,JustOne=False):
    r"""
    Returns one or all isomorphisms between two elliptic curves.

    INPUT:

    - ``E``, ``F`` (EllipticCurve) -- Two elliptic curves.

    - ``JustOne`` (bool) If True, returns one isomorphism, or None if
      the curves are not isomorphic.  If False, returns a (possibly
      empty) list of isomorphisms.

    OUTPUT:

    Either None, or a 4-tuple `(u,r,s,t)` representing an isomorphism,
    or a list of these.

    .. note::

       This function is not intended for users, who should use the
       interface provided by ``ell_generic``.

    EXAMPLES::

        sage: from sage.schemes.elliptic_curves.ell_curve_isogeny_new import isomorphisms
        sage: isomorphisms(EllipticCurve_from_j(0),EllipticCurve('27a3'))
        [(-1, 0, 0, -1), (1, 0, 0, 0)]
        sage: isomorphisms(EllipticCurve_from_j(0),EllipticCurve('27a3'),JustOne=True)
        (1, 0, 0, 0)
        sage: isomorphisms(EllipticCurve_from_j(0),EllipticCurve('27a1'))
        []
        sage: isomorphisms(EllipticCurve_from_j(0),EllipticCurve('27a1'),JustOne=True)
    """
#    from ell_generic import EllipticCurve_generic
#    if not isinstance(E, EllipticCurve_generic) or not isinstance(F, EllipticCurve_generic):
#        raise ValueError, "arguments are not elliptic curves"
    K = E.base_ring()
#   if not K == F.base_ring(): return []
    j=E.j_invariant()
    if  j != F.j_invariant():
        if JustOne: return None
        return []

    from sage.rings.all import PolynomialRing
    x=PolynomialRing(K,'x').gen()

    a1E, a2E, a3E, a4E, a6E = E.ainvs()
    a1F, a2F, a3F, a4F, a6F = F.ainvs()

    char=K.characteristic()

    if char==2:
        if j==0:
            ulist=(x**3-(a3E/a3F)).roots(multiplicities=False)
            ans=[]
            for u in ulist:
                slist=(x**4+a3E*x+(a2F**2+a4F)*u**4+a2E**2+a4E).roots(multiplicities=False)
                for s in slist:
                    r=s**2+a2E+a2F*u**2
                    tlist= (x**2 + a3E*x + r**3 + a2E*r**2 + a4E*r + a6E + a6F*u**6).roots(multiplicities=False)
                    for t in tlist:
                        if JustOne: return (u,r,s,t)
                        ans.append((u,r,s,t))
            if JustOne: return None
            ans.sort()
            return ans
        else:
            ans=[]
            u=a1E/a1F
            r=(a3E+a3F*u**3)/a1E
            slist=[s[0] for s in (x**2+a1E*x+(r+a2E+a2F*u**2)).roots()]
            for s in slist:
                t = (a4E+a4F*u**4 + s*a3E + r*s*a1E + r**2)
                if JustOne: return (u,r,s,t)
                ans.append((u,r,s,t))
            if JustOne: return None
            ans.sort()
            return ans

    b2E, b4E, b6E, b8E      = E.b_invariants()
    b2F, b4F, b6F, b8F      = F.b_invariants()

    if char==3:
        if j==0:
            ulist=(x**4-(b4E/b4F)).roots(multiplicities=False)
            ans=[]
            for u in ulist:
                s=a1E-a1F*u
                t=a3E-a3F*u**3
                rlist=(x**3-b4E*x+(b6E-b6F*u**6)).roots(multiplicities=False)
                for r in rlist:
                    if JustOne: return (u,r,s,t+r*a1E)
                    ans.append((u,r,s,t+r*a1E))
            if JustOne: return None
            ans.sort()
            return ans
        else:
            ulist=(x**2-(b2E/b2F)).roots(multiplicities=False)
            ans=[]
            for u in ulist:
                r = (b4F*u**4 -b4E)/b2E
                s = (a1E-a1F*u)
                t = (a3E-a3F*u**3 + a1E*r)
                if JustOne: return (u,r,s,t)
                ans.append((u,r,s,t))
            if JustOne: return None
            ans.sort()
            return ans

# now char!=2,3:
    c4E,c6E = E.c_invariants()
    c4F,c6F = F.c_invariants()

    if j==0:
        m,um = 6,c6E/c6F
    elif j==1728:
        m,um=4,c4E/c4F
    else:
        m,um=2,(c6E*c4F)/(c6F*c4E)
    ulist=(x**m-um).roots(multiplicities=False)
    ans=[]
    for u in ulist:
        s = (a1F*u - a1E)/2
        r = (a2F*u**2 + a1E*s + s**2 - a2E)/3
        t = (a3F*u**3 - a1E*r - a3E)/2
        if JustOne: return (u,r,s,t)
        ans.append((u,r,s,t))
    if JustOne: return None
    ans.sort()
    return ans
