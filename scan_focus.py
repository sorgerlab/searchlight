"Launch test_focus.py jobs via LSF on Orchestra."

import os
import sys
import numpy as np

testing_mode = False
if sys.argv[-1] == 'test':
    sys.argv.pop()
    testing_mode = True
    print "TEST MODE (will not run any commands)"

bsub_args = ' '.join(sys.argv[1:])
basepath = os.path.dirname(os.path.abspath(__file__))

NSTEPS = 41
ff_values = np.linspace(1, 3, NSTEPS)

for ff in ff_values:

    # Make sure we are getting the "round" numbers we expect.
    ff_16g = '%.16g' % ff
    assert len(ff_16g) <= 4, "Unexpected focus_factor value: %s" % ff_16g

    cmd = ("bsub %(bsub_args)s %(executable)s %(basepath)s/test_focus.py %(ff).2f" %
           dict(executable=sys.executable, **locals()))
    print ">", cmd
    if not testing_mode:
        os.system(cmd)
