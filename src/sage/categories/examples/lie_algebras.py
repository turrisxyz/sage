r"""
Examples of a Lie algebra
"""
#*****************************************************************************
#  Copyright (C) 2014 Travis Scrimshaw <tscrim at ucdavis.edu>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
#*****************************************************************************

#from sage.misc.cachefunc import cached_method
from sage.sets.family import Family
from sage.categories.all import LieAlgebras
from sage.structure.parent import Parent
from sage.structure.unique_representation import UniqueRepresentation
from sage.structure.element_wrapper import ElementWrapper

class LieAlgebraFromAssociative(Parent, UniqueRepresentation):
    r"""
    An example of a Lie algebra: a Lie algebra generated by
    a set of elements of an associative algebra.

    This class illustrates a minimal implementation of a Lie algebra.

    Let `R` be a commutative ring, and `A` an associative
    `R`-algebra. The Lie algebra `A` (sometimes denoted `A^-`)
    is defined to be the `R`-module `A` with Lie bracket given by
    the commutator in `A`: that is, `[a, b] := ab - ba` for all
    `a, b \in A`.

    What this class implements is not precisely `A^-`, however;
    it is the Lie subalgebra of `A^-` generated by the elements
    of the iterable ``gens``. This specific implementation does not
    provide a reasonable containment test (i.e., it does not allow
    you to check if a given element `a` of `A^-` belongs to this
    Lie subalgebra); it, however, allows computing inside it.

    INPUT:

    - ``gens`` -- a nonempty iterable consisting of elements of an
      associative algebra `A`

    OUTPUT:

    The Lie subalgebra of `A^-` generated by the elements of
    ``gens``

    EXAMPLES:

    We create a model of `\mathfrak{sl}_2` using matrices::

        sage: gens = [matrix([[0,1],[0,0]]), matrix([[0,0],[1,0]]), matrix([[1,0],[0,-1]])]
        sage: for g in gens:
        ....:     g.set_immutable()
        sage: L = LieAlgebras(QQ).example(gens)
        sage: e,f,h = L.lie_algebra_generators()
        sage: e.bracket(f) == h
        True
        sage: h.bracket(e) == 2*e
        True
        sage: h.bracket(f) == -2*f
        True
    """
    @staticmethod
    def __classcall_private__(cls, gens):
        """
        Normalize input to ensure a unique representation.

        EXAMPLES::

            sage: S3 = SymmetricGroupAlgebra(QQ, 3)
            sage: L1 = LieAlgebras(QQ).example()
            sage: gens = list(S3.algebra_generators())
            sage: L2 = LieAlgebras(QQ).example(gens)
            sage: L1 is L2
            True
        """
        return super(LieAlgebraFromAssociative, cls).__classcall__(cls, tuple(gens))

    def __init__(self, gens):
        """
        EXAMPLES::

            sage: L = LieAlgebras(QQ).example()
            sage: TestSuite(L).run()
        """
        if not gens:
            raise ValueError("need at least one generator")
        self._gens = gens
        self._A = gens[0].parent()
        R = self._A.base_ring()
        Parent.__init__(self, base=R, category=LieAlgebras(R))

    def _repr_(self):
        """
        EXAMPLES::

            sage: LieAlgebras(QQ).example()
            An example of a Lie algebra: the Lie algebra from the associative algebra
             Symmetric group algebra of order 3 over Rational Field
             generated by ([2, 1, 3], [2, 3, 1])
        """
        return "An example of a Lie algebra: the Lie algebra from the" \
               " associative algebra {} generated by {}".format(
                    self._A, self._gens)

    def _element_constructor_(self, value):
        """
        Return an element of ``self``.

        EXAMPLES::

            sage: S3 = SymmetricGroupAlgebra(ZZ, 3)
            sage: gens = S3.algebra_generators()
            sage: L = LieAlgebras(QQ).example()
            sage: L(3*gens[0] + gens[1])
            3*[2, 1, 3] + [2, 3, 1]
        """
        return self.element_class(self, self._A(value))

    def zero(self):
        """
        Return the element 0.

        EXAMPLES::

            sage: L = LieAlgebras(QQ).example()
            sage: L.zero()
            0
        """
        return self.element_class(self, self._A.zero())

    def lie_algebra_generators(self):
        """
        Return the generators of ``self`` as a Lie algebra.

        EXAMPLES::

            sage: L = LieAlgebras(QQ).example()
            sage: L.lie_algebra_generators()
            Family ([2, 1, 3], [2, 3, 1])
        """
        return Family([self.element_class(self, g) for g in self._gens])

    # TODO: refactor to use LieAlgebraElementWrapper once more of #14901 is added in
    class Element(ElementWrapper):
        """
        Wrap an element as a Lie algebra element.
        """
        def __eq__(self, rhs):
            """
            Check equality.

            This check is rather restrictive: ``self`` and ``rhs`` are only
            revealed as equal if they are equal *and* have the same parent
            (or both are zero).

            EXAMPLES::

                sage: L = LieAlgebras(QQ).example()
                sage: x,y = L.lie_algebra_generators()
                sage: x == x
                True
                sage: x.bracket(y) == -y.bracket(x)
                True
                sage: x == y
                False
                sage: x.bracket(x) == L.zero()
                True
                sage: x.bracket(x) == 0
                True
            """
            if not isinstance(rhs, LieAlgebraFromAssociative.Element):
                return self.value == 0 and rhs == 0
            return self.parent() == rhs.parent() and self.value == rhs.value

        def __ne__(self, rhs):
            """
            Check not-equals.

            EXAMPLES::

                sage: L = LieAlgebras(QQ).example()
                sage: x,y = L.lie_algebra_generators()
                sage: x != y
                True
                sage: x != 0
                True
                sage: x != x
                False
                sage: x.bracket(y) != -y.bracket(x)
                False
            """
            return not self.__eq__(rhs)

        def __bool__(self):
            """
            Check non-zero.

            EXAMPLES::

                sage: L = LieAlgebras(QQ).example()
                sage: bool(sum(L.lie_algebra_generators()))
                True
                sage: bool(L.zero())
                False
            """
            return bool(self.value)

        

        def _add_(self, rhs):
            """
            Add ``self`` and ``rhs``.

            EXAMPLES::

                sage: L = LieAlgebras(QQ).example()
                sage: x,y = L.lie_algebra_generators()
                sage: x + y
                [2, 1, 3] + [2, 3, 1]
            """
            return self.__class__(self.parent(), self.value + rhs.value)

        def _sub_(self, rhs):
            """
            Subtract ``self`` and ``rhs``.

            EXAMPLES::

                sage: L = LieAlgebras(QQ).example()
                sage: x,y = L.lie_algebra_generators()
                sage: x - y
                [2, 1, 3] - [2, 3, 1]
            """
            return self.__class__(self.parent(), self.value - rhs.value)

        def _acted_upon_(self, scalar, self_on_left=False):
            """
            Return the action of a scalar on ``self``.

            EXAMPLES::

                sage: L = LieAlgebras(QQ).example()
                sage: x,y = L.lie_algebra_generators()
                sage: 3 * x
                3*[2, 1, 3]
            """
            # This was copied, but IDK if it still applies:
            # With the current design, the coercion model does not have
            # enough information to detect apriori that this method only
            # accepts scalars; so it tries on some elements(), and we need
            # to make sure to report an error.
            if hasattr( scalar, 'parent' ) and scalar.parent() != self.base_ring():
                # Temporary needed by coercion (see Polynomial/FractionField tests).
                if self.base_ring().has_coerce_map_from(scalar.parent()):
                    scalar = self.base_ring()( scalar )
                else:
                    return None
            if self_on_left:
                return self.__class__(self.parent(), self.value * scalar)
            return self.__class__(self.parent(), scalar * self.value)

        def __truediv__(self, x, self_on_left=False):
            """
            Division by coefficients.

            EXAMPLES::

                sage: L = LieAlgebras(QQ).example()
                sage: x,y = L.lie_algebra_generators()
                sage: y / 4
                1/4*[2, 3, 1]
            """
            if self_on_left:
                return self * (~x)
            return (~x) * self

        def __neg__(self):
            """
            Return the negation of ``self``.

            EXAMPLES::

                sage: L = LieAlgebras(QQ).example()
                sage: x,y = L.lie_algebra_generators()
                sage: -x
                -[2, 1, 3]
            """
            return self.__class__(self.parent(), -self.value)

        def __getitem__(self, i):
            """
            Redirect the ``__getitem__()`` to the wrapped element.

            EXAMPLES::

                sage: gens = [matrix([[0,1],[0,0]]), matrix([[0,0],[1,0]]), matrix([[1,0],[0,-1]])]
                sage: for g in gens:
                ....:     g.set_immutable()
                sage: L = LieAlgebras(QQ).example(gens)
                sage: e,f,h = L.lie_algebra_generators()
                sage: h[0,0]
                1
                sage: h[1,1]
                -1
                sage: h[0,1]
                0
            """
            return self.value.__getitem__(i)

        def _bracket_(self, rhs):
            """
            Return the Lie bracket ``[self, rhs]``.

            EXAMPLES::

                sage: L = LieAlgebras(QQ).example()
                sage: x,y = L.lie_algebra_generators()
                sage: elt = 2*x - y
                sage: elt.bracket(elt)
                0
                sage: elt.bracket(x)
                -[1, 3, 2] + [3, 2, 1]
                sage: elt2 = x.bracket(y) + x
                sage: elt.bracket(elt2)
                -2*[2, 1, 3] + 4*[2, 3, 1] - 4*[3, 1, 2] + 2*[3, 2, 1]
            """
            return self.__class__(self.parent(), self.value * rhs.value - rhs.value * self.value)

Example = LieAlgebraFromAssociative
