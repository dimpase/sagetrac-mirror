from cpython.object cimport PyObject, PyTypeObject, destructor

cdef class Pool:
    cdef object __weakref__

    cdef bint enabled
    cdef PyTypeObject* type

    cdef PyObject** elements
    cdef long size
    cdef long allocated

    cdef destructor save_tp_dealloc

    cdef Pool new_enabled(self)


cdef PY_NEW_FROM_POOL(Pool)

cdef pool_disabled(type t)
cdef pool_enabled(Pool pool, length, bint is_global)

