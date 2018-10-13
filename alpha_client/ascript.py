import config
import sys
from probability import two_week_return_by_performance_period


''' argparse might be preferable. see https://stackoverflow.com/questions/30392793/input-variable-from-command-line-in-python '''

if (len(sys.argv) > 1):
    config.old = sys.argv[1]

print (config.old)

two_week_return_by_performance_period()

# python -m pdb -c continue ascript.py 999


