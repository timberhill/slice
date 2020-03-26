# slice

This is a piece of code published alongside the paper _Lisogorskyi et al. 2019, MNRAS, 485, 4804_ (DOI:[10.1093/mnras/stz694](https://doi.org/10.1093/mnras/stz694), arXiv:[1902.10711](https://arxiv.org/abs/1902.10711)).

The code measures active lines equivalent width changes and asymmetries in HARPS (High Accuracy Radial Velocity Planet Searcher) spectra. These lines were identified as "active" using 2010 observations of α Centauri B (see the paper for details). Some example spectra are included in this repository.

## Dependencies

Python 3.x and packages:

- numpy
- pandas
- scipy
- astropy
- matplotlib
- joblib

## Usage

The code is not a package and doesn't need installation, just clone the repository.

### run

To run, go to the `code` folder and run the example with
```bash
$ python main.py
```

### results

The results are written to the `data/results.dat` file. It will contain a table with all the spectral lines.
The columns are:

`name`, `center` - species and rest frame wavelength of a line in Angstrom

`ew`, `ew_diff` - equivalent width and the amplitude of its variation, in Angstrom

`asym_diff` - amplitude of asymmetry variation, measures as flux difference between thr right and left wings of a line

`logS_ew_p`, `logS_ew_pp` - two-tailed Pearson correlation, S-index and equivalent width of the line

`logS_asym_p`, `logS_asym_pp` - two-tailed Pearson correlation, S-index and asymmetry of the line

`rv_ew_p`, `rv_ew_pp` - two-tailed Pearson correlation, radial velocity and equivalent width of the line

`rv_asym_p`, `rv_asym_pp` - two-tailed Pearson correlation, radial velocity and asymmetry of the line

Time series results of each line is in `data/results` folder, filenames containing wavelength of the line in 100 * Angstrom (to avoid decimal point) and the species of the line for readability. 
Each file contains:

`filename` - name of the spectrum file the value was measured from

`bjd` - Barycentric Julian Date, in days

`ew` - equivalent width of the line in Angstrom

`asym` - asymmetry of the line

### settings

The code relies on a few settings (and files) that have default values for demonstration purposes.
These are set in `code.settings.py`:

`lines_list_path` - a file containing the list of lines to measure and spectral ranges to measure the continuum and the line from, defined by 6 wavelengths from left to right _(default/example: `../data/active_lines.dat`)_

`list_path` - radial velocity and S-index values for the spectra _(default/example: `../data/rvdata.dat`)_

`s1d_folder` - folder containing the `_s1d_` spectra _(default/example: `../data/s1d/`)_

`output_path` - output directory for the individual line files _(default/example: `../data/results/`)_

`summary_file` - summarized table with variation fo all the lines _(default/example: `../data/results.dat`)_

`plots_path` - output plots directory _(default/example: `../data/plots/`)_

`template_n` - number of spectra with the lowest S-index to average for a low activity template _(default/example: 20)_

`ncores` - number of cores to utilize _(default/example: 2)_
