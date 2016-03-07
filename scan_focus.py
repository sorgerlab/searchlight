"Launch test_focus.py jobs via LSF on Orchestra."

import os
import sys
import numpy as np

testing_mode = False
if len(sys.argv) == 2 and sys.argv[1] == 'test':
    testing_mode = True
    print "TEST MODE (will not run any commands)"

ff_values = np.linspace(1, 3, 41)

for ff in ff_values:

    # Make sure we are getting the "round" numbers we expect.
    ff_16g = '%.16g' % ff
    assert len(ff_16g) <= 4, "Unexpected focus_factor value: %s" % ff_16g

    cmd = "python test_focus.py %.2f" % ff
    print ">", cmd
    if not testing_mode:
        os.system(cmd)
