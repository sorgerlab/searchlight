import numpy as np
cimport numpy as np
cimport cython
from cython.parallel import parallel, prange
from libc.math cimport fabs

DTYPE = np.float
ctypedef np.float_t DTYPE_t

@cython.boundscheck(False)
def searchlight(DTYPE_t[:, ::1] cc1,
                DTYPE_t[:, ::1] cc2,
                DTYPE_t[:] f):
    assert cc1.shape[1] == cc2.shape[1] == f.shape[0]
    cdef int sum = 0
    cdef Py_ssize_t ndims = cc1.shape[1]
    cdef Py_ssize_t ncc1 = cc1.shape[0]
    cdef Py_ssize_t ncc2 = cc2.shape[0]
    cdef Py_ssize_t i1, i2, dim
    with nogil:
        for i1 in prange(ncc1, schedule='guided'):
            for i2 in range(ncc2):
                for dim in range(ndims):
                    if fabs(cc1[i1,dim]-cc2[i2,dim]) > f[dim]:
                        break
                else:
                    sum += 1
    return sum
