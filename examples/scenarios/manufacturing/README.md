# Synthetic sampling accuracy lab

Run from the repository root with:

```sh
python examples/scenarios/manufacturing/sampling_accuracy_lab.py
python -m unittest discover -s tests -p 'test_sampling_accuracy_lab.py' -v
```

The lab is deterministic, uses only Python's standard library, and makes no model
or network calls. It checks the existing exact known-WIP sampling rule, then reports
separate MAE/RMSE results for an empirical arrival-lead baseline, a small ridge
regression, and a seasonal-naive forecast. A seeded weekday Poisson simulation and
a training-residual conformal interval report empirical holdout coverage.

The daily-count evaluation uses the first 84 synthetic days for fitting and the next
28 for scoring. The arrival case estimates weekday demand and lead-time probabilities
from orders known to have arrived before the cutoff. No held-out row is passed to a
fitter. The interval coverage and error values describe this one synthetic fixture;
they do not establish calibrated uncertainty, manufacturing value, accuracy gains,
or any preferred external package. No real fab behavior, data, or sampling policy is
represented. Replace the synthetic fixture and acceptance criteria with approved,
historically time-split company data before making operational decisions.
