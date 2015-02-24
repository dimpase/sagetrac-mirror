from free_module_element cimport FreeModuleElement
from sage.ext.mod_int cimport *

cdef class Vector_modn_dense(FreeModuleElement):
    cdef mod_int* _entries
    cdef mod_int _p
    cdef object _base_ring

    cdef _new_c(self)
    cdef _init(self, Py_ssize_t degree, parent, mod_int p)

