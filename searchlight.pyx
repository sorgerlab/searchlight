import numpy as np
cimport numpy as np
cimport cython
from cython.parallel import parallel, prange
from libc.math cimport fabs

DTYPE = np.float
ctypedef np.float_t DTYPE_t

def searchlight(cc1, cc2, f):
    # The cython argument typing in searchlight_core raises an exception if cc1
    # or cc2 are zero-length, so we need to handle that case in a non-optimized
    # function.
    if len(cc1) > 0 and len(cc2) > 0:
        return searchlight_core(cc1, cc2, f)
    else:
        return 0

@cython.boundscheck(False)
def searchlight_core(DTYPE_t[:, ::1] cc1,
                DTYPE_t[:, ::1] cc2,
                DTYPE_t[:] f):
    assert cc1.shape[1] == cc2.shape[1] == f.shape[0]
    cdef unsigned long sum = 0
    cdef size_t ndims = cc1.shape[1]
    cdef size_t ncc1 = cc1.shape[0]
    cdef size_t ncc2 = cc2.shape[0]
    cdef size_t i1, i2, dim
    with nogil:
        for i1 in prange(ncc1, schedule='guided'):
            for i2 in range(ncc2):
                for dim in range(ndims):
                    if fabs(cc1[i1,dim]-cc2[i2,dim]) > f[dim]:
                        break
                else:
                    sum += 1
    return sum
