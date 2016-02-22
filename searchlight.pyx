import numpy as np
cimport numpy as np
cimport cython

# def searchlight1(cc1, cc2, f):
#     sum = 0
#     for c1 in cc1:
#         for c2 in cc2:
#             for v1, v2, vf in zip(c1, c2, f):
#                 if abs(v1-v2) > vf:
#                     break
#             else:
#                 sum += 1
#     return sum

# def searchlight2(cc1, cc2, f):
#     sum = 0
#     for c1 in cc1:
#         for c2 in cc2:
#             sum += np.all(abs(c1-c2) <= f)
#     return sum

DTYPE = np.float
ctypedef np.float_t DTYPE_t

@cython.boundscheck(False)
def searchlight1_opt(np.ndarray[DTYPE_t, ndim=2] cc1,
                     np.ndarray[DTYPE_t, ndim=2] cc2,
                     np.ndarray[DTYPE_t] f):
    assert cc1.dtype == cc2.dtype == f.dtype == DTYPE
    assert cc1.shape[1] == cc2.shape[1] == f.shape[0]
    cdef int sum = 0
    cdef Py_ssize_t ndims = cc1.shape[1]
    cdef Py_ssize_t ncc1 = cc1.shape[0]
    cdef Py_ssize_t ncc2 = cc2.shape[0]
    cdef Py_ssize_t i1, i2, dim
    for i1 in range(ncc1):
        for i2 in range(ncc2):
            for dim in range(ndims):
                if abs(cc1[i1,dim]-cc2[i2,dim]) > f[dim]:
                    break
            else:
                sum += 1
    return sum
