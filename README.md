py-semver
=========

A python port of the node.js semver library. 

## Usage
py-semver doesn't yet have a setup.py, so just pop it in your working directory. Then:

	import semver
	semver.valid('1.2.3') // '1.2.3'
    semver.valid('a.b.c') // False
    semver.clean('  =v1.2.3   ') // '1.2.3'
    semver.satisfies('1.2.3', '1.x || >=2.5.0 || 5.0.0 - 7.2.3') // True
    semver.gt('1.2.3', '9.8.7') // False
    semver.lt('1.2.3', '9.8.7') // True
    semver.inc('1.2.3', 'major') // '2.0.0'

py-semver is designed to operate as similarly as possible to [isaacs/node-semver](https://github.com/isaacs/node-semver). 

## Versions & Ranges
See the "versions" and "ranges" sections of [isaacs/node-semver](https://github.com/isaacs/node-semver).

## Tests
Run test.py; no output is good output. The tests defined in in tests.py are (nearly) identical to those defined by node-semver.