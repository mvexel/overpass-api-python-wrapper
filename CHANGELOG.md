# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased](https://github.com/mvexel/overpass-api-python-wrapper/compare/v0.7.2...HEAD)

## [v0.7.2](https://github.com/mvexel/overpass-api-python-wrapper/compare/0.7.1...v0.7.2) - 2024-08-10

### Commits

- Can't just go ahead and change the license :) [`39f7150`](https://github.com/mvexel/overpass-api-python-wrapper/commit/39f71509a7b5640a55af01ac77ab437ac44796d1)
- chore:add homepage to toml [`c62678e`](https://github.com/mvexel/overpass-api-python-wrapper/commit/c62678e7c89ec55b45cf98223ba0202492e3b91f)

## [0.7.1](https://github.com/mvexel/overpass-api-python-wrapper/compare/0.7.0...0.7.1) - 2024-08-10

### Merged

- Make tests run again [`#167`](https://github.com/mvexel/overpass-api-python-wrapper/pull/167)
- switch to poetry. tests are failing right now but we'll fix that next [`#166`](https://github.com/mvexel/overpass-api-python-wrapper/pull/166)
- Few minor Python 3 code modernizations [`#160`](https://github.com/mvexel/overpass-api-python-wrapper/pull/160)
- Add Python 3.11, drop below 3.8, update deps [`#159`](https://github.com/mvexel/overpass-api-python-wrapper/pull/159)
- Update README.md [`#162`](https://github.com/mvexel/overpass-api-python-wrapper/pull/162)
- Convenience properties for when API is next available [`#150`](https://github.com/mvexel/overpass-api-python-wrapper/pull/150)
- Handle variable numbers of lines in Overpass status page [`#152`](https://github.com/mvexel/overpass-api-python-wrapper/pull/152)
- documentation update to clarify CSV output [`#146`](https://github.com/mvexel/overpass-api-python-wrapper/pull/146)
- Leveraging pytest features [`#141`](https://github.com/mvexel/overpass-api-python-wrapper/pull/141)
- Include nodes, user, uid, timestamp, and version in GeoJSON properties [`#130`](https://github.com/mvexel/overpass-api-python-wrapper/pull/130)
- Add tox and Github Actions [`#131`](https://github.com/mvexel/overpass-api-python-wrapper/pull/131)
- Fix and modernize Travis CI [`#132`](https://github.com/mvexel/overpass-api-python-wrapper/pull/132)
- List comprehension, literal comparison, import ordering, staticmethod [`#133`](https://github.com/mvexel/overpass-api-python-wrapper/pull/133)
- Methods to check API status [`#134`](https://github.com/mvexel/overpass-api-python-wrapper/pull/134)
- GeoJson MultiPolygon errors with duplicate IDs [`#129`](https://github.com/mvexel/overpass-api-python-wrapper/pull/129)
- Add date parameter to query builder [`#125`](https://github.com/mvexel/overpass-api-python-wrapper/pull/125)
- Drop python v2.7 and v3.3 from tests, add v3.7–3.8 [`#128`](https://github.com/mvexel/overpass-api-python-wrapper/pull/128)
- Relation and multipolygon support [`#115`](https://github.com/mvexel/overpass-api-python-wrapper/pull/115)

### Commits

- Use mock response for basic geojson test [`b83016d`](https://github.com/mvexel/overpass-api-python-wrapper/commit/b83016dc169da8d6191da38305e603d3044a2767)
- merge main into #140 [`ca2d57e`](https://github.com/mvexel/overpass-api-python-wrapper/commit/ca2d57edec65ebcdc3a38e113ea1c8c710ea9667)
- Parameterized geojson_extended test [`2c7926b`](https://github.com/mvexel/overpass-api-python-wrapper/commit/2c7926ba9130d2ab088c6e165a6e0f1f450cc22a)

## [0.7.0](https://github.com/mvexel/overpass-api-python-wrapper/compare/0.6.1...0.7.0) - 2019-12-10

### Merged

- Relation and multipolygon support [`#115`](https://github.com/mvexel/overpass-api-python-wrapper/pull/115)
- Added some docstrings to API and get() method [`#113`](https://github.com/mvexel/overpass-api-python-wrapper/pull/113)
- Fix typo in README.md [`#114`](https://github.com/mvexel/overpass-api-python-wrapper/pull/114)
-  Added ability to set headers of request [`#110`](https://github.com/mvexel/overpass-api-python-wrapper/pull/110)
- New example `plot_state_border` [`#107`](https://github.com/mvexel/overpass-api-python-wrapper/pull/107)

### Commits

- Bugfixed and cleaned up _as_geojson method [`5fabd38`](https://github.com/mvexel/overpass-api-python-wrapper/commit/5fabd38b65ceeb06e2aa9b8310c8639e1aff9077)
- added support for multipolygons [`51c4ae9`](https://github.com/mvexel/overpass-api-python-wrapper/commit/51c4ae9ecd42e1bc377b802651ad84c2db058964)
- added support for relations [`4a61d9f`](https://github.com/mvexel/overpass-api-python-wrapper/commit/4a61d9f3c4b9254db63f6daad81275763474f1b1)

## [0.6.1](https://github.com/mvexel/overpass-api-python-wrapper/compare/0.6.0...0.6.1) - 2018-08-29

### Merged

- Fixed api output for build=False #93 [`#97`](https://github.com/mvexel/overpass-api-python-wrapper/pull/97)
- Requests proxy support [`#86`](https://github.com/mvexel/overpass-api-python-wrapper/pull/86)

### Fixed

- adding examples and tests dirs to distribution, bumping to 0.6.1, fixes #50 [`#50`](https://github.com/mvexel/overpass-api-python-wrapper/issues/50)
- strip whitespace, fixes #101 [`#101`](https://github.com/mvexel/overpass-api-python-wrapper/issues/101)
- fix example, fixes #95 [`#95`](https://github.com/mvexel/overpass-api-python-wrapper/issues/95)
- include test dir in manifest, fixes #50 [`#50`](https://github.com/mvexel/overpass-api-python-wrapper/issues/50)
- add copyright to code, add LICENSE to manifest, fixes #51 [`#51`](https://github.com/mvexel/overpass-api-python-wrapper/issues/51)
- re-adding RST doc (generated using pandoc from md file), fixes #67 [`#67`](https://github.com/mvexel/overpass-api-python-wrapper/issues/67)

### Commits

- reformatting and correctly routing xml responseformat [`c8f96ff`](https://github.com/mvexel/overpass-api-python-wrapper/commit/c8f96ff0bdc89db32b03def5a56fa06fb48fde2e)
- improvements on documentation [`afbaa5d`](https://github.com/mvexel/overpass-api-python-wrapper/commit/afbaa5d2ff0c99dddd252f557a6fc4ddd604562d)
- Updating README and examples [`f07db0d`](https://github.com/mvexel/overpass-api-python-wrapper/commit/f07db0d6e090a93c10ded4a50b2665c9682599f4)

## [0.6.0](https://github.com/mvexel/overpass-api-python-wrapper/compare/0.5.7...0.6.0) - 2018-04-06

### Commits

- hotfix and fix tests [`b77865a`](https://github.com/mvexel/overpass-api-python-wrapper/commit/b77865a5d18620f83b41216bb420b324af2d6b54)
- fixing var name in test script and remove function call [`198aeb2`](https://github.com/mvexel/overpass-api-python-wrapper/commit/198aeb212c2d0ae9d58ca8333bc66395cd10b9f1)
- update travis build config [`db73fa3`](https://github.com/mvexel/overpass-api-python-wrapper/commit/db73fa3bf98e77d4733c5842c440e07e0e2c21bb)

## [0.5.7](https://github.com/mvexel/overpass-api-python-wrapper/compare/0.5.6...0.5.7) - 2018-04-06

### Merged

- fix bug in complete ways and relations query [`#75`](https://github.com/mvexel/overpass-api-python-wrapper/pull/75)
- Fix broken link in readme. [`#68`](https://github.com/mvexel/overpass-api-python-wrapper/pull/68)
- Revert "Change to https as http is no longer supported on overpass-ap… [`#65`](https://github.com/mvexel/overpass-api-python-wrapper/pull/65)

### Fixed

- Remove superfluous &gt; chars, fixes #84 [`#84`](https://github.com/mvexel/overpass-api-python-wrapper/issues/84)
- Verbosity for GeoJSON output [`#79`](https://github.com/mvexel/overpass-api-python-wrapper/issues/79)
- logging compatible with py3, fixes #72 [`#72`](https://github.com/mvexel/overpass-api-python-wrapper/issues/72)

### Commits

- support CSV [`d833dd3`](https://github.com/mvexel/overpass-api-python-wrapper/commit/d833dd361ec09803209413b546b94fddee529a5f)
- http &gt; https and some minor formatting [`c7b5bf8`](https://github.com/mvexel/overpass-api-python-wrapper/commit/c7b5bf850e214f9268b6298b8400ad01669d45d1)
- adding example [`bbc97b3`](https://github.com/mvexel/overpass-api-python-wrapper/commit/bbc97b30a8ab970798643bccf19cfd2a8eed37b2)

## [0.5.6](https://github.com/mvexel/overpass-api-python-wrapper/compare/0.5.5...0.5.6) - 2016-08-22

### Commits

- simplify setup.py so that it actually works... [`3cdf157`](https://github.com/mvexel/overpass-api-python-wrapper/commit/3cdf15739980bb9f4a9bda4f50a1cc4e70986684)

## [0.5.5](https://github.com/mvexel/overpass-api-python-wrapper/compare/0.4.0...0.5.5) - 2016-08-21

### Merged

- Support for full multiline query [`#57`](https://github.com/mvexel/overpass-api-python-wrapper/pull/57)
- enable csv response format [`#60`](https://github.com/mvexel/overpass-api-python-wrapper/pull/60)
- Change to https as http is no longer supported on overpass-api.de [`#63`](https://github.com/mvexel/overpass-api-python-wrapper/pull/63)

### Commits

- version 0.5.0 [`1051aba`](https://github.com/mvexel/overpass-api-python-wrapper/commit/1051aba45a2b38079c948fa4bfd8581c95dd81c4)
- bumping to 0.5.4, getting markdown to rst to work for PyPi [`cfb9407`](https://github.com/mvexel/overpass-api-python-wrapper/commit/cfb9407d19b37c1022d508e133c64dce14fe1d74)
- Working [`a45480e`](https://github.com/mvexel/overpass-api-python-wrapper/commit/a45480e6613723c3f8112a8f8b4523cd6ab2cf15)

## [0.4.0](https://github.com/mvexel/overpass-api-python-wrapper/compare/0.1.0...0.4.0) - 2016-03-31

### Merged

- Added verbosity options to the return [`#47`](https://github.com/mvexel/overpass-api-python-wrapper/pull/47)
- fixes obvious error in example, see #37 [`#44`](https://github.com/mvexel/overpass-api-python-wrapper/pull/44)
- Merge Wille's fork and improvements [`#36`](https://github.com/mvexel/overpass-api-python-wrapper/pull/36)
- Handle server runtime error from overpass API [`#35`](https://github.com/mvexel/overpass-api-python-wrapper/pull/35)
- Fix response encoding (fixing #34) [`#34`](https://github.com/mvexel/overpass-api-python-wrapper/pull/34)
- Substitute post for get.  Received 414 error when requesting large poly [`#26`](https://github.com/mvexel/overpass-api-python-wrapper/pull/26)
- Implemented exceptions. [`#25`](https://github.com/mvexel/overpass-api-python-wrapper/pull/25)

### Commits

- raw commit [`dc960be`](https://github.com/mvexel/overpass-api-python-wrapper/commit/dc960beb899537aa64a9a61bbc39160daa1e7906)
- Implemented an exceptions class for every kind of error. [`fcd49d6`](https://github.com/mvexel/overpass-api-python-wrapper/commit/fcd49d67e5fe6c1695b7fd31b6f3f6c180da75d3)
- response format flexibility [`98b6f63`](https://github.com/mvexel/overpass-api-python-wrapper/commit/98b6f63f3ce486d15aa619f8a60a0ad268983230)

## [0.1.0](https://github.com/mvexel/overpass-api-python-wrapper/compare/0.0.2...0.1.0) - 2014-12-04

### Commits

- bumping version to 0.1.0, ready for pypi [`90e3913`](https://github.com/mvexel/overpass-api-python-wrapper/commit/90e3913ca6b9d39ec8fed5fbbde195144293ba81)
- bumping to 0.0.2 [`7660f3e`](https://github.com/mvexel/overpass-api-python-wrapper/commit/7660f3ecc0c38c2f4ebdf86c618efc08f6737ebf)

## [0.0.2](https://github.com/mvexel/overpass-api-python-wrapper/compare/0.0.1...0.0.2) - 2014-11-24

### Merged

- no emails from travis [`#22`](https://github.com/mvexel/overpass-api-python-wrapper/pull/22)
- p3 compatibility + some formatting + removing unused import [`#21`](https://github.com/mvexel/overpass-api-python-wrapper/pull/21)
- Simple queries [`#13`](https://github.com/mvexel/overpass-api-python-wrapper/pull/13)
- Auto import [`#11`](https://github.com/mvexel/overpass-api-python-wrapper/pull/11)
- Allow newer version of requests [`#12`](https://github.com/mvexel/overpass-api-python-wrapper/pull/12)
- Enable syntax highlighting for code snippets. [`#10`](https://github.com/mvexel/overpass-api-python-wrapper/pull/10)
- Fix installation failure on case-sensitive file systems. [`#9`](https://github.com/mvexel/overpass-api-python-wrapper/pull/9)

### Commits

- First crack at geoJSON output [`ebedee0`](https://github.com/mvexel/overpass-api-python-wrapper/commit/ebedee01b48657426a00c9f38195ab82c33cf3d9)
- merging pep8 changes from #19 [`f99f3fc`](https://github.com/mvexel/overpass-api-python-wrapper/commit/f99f3fc45e36da021aed01f4b72ea53c7aea5dcf)
- Setting 'out geometry;' on asGeoJSON=True queries - geoJSON output [`20c1582`](https://github.com/mvexel/overpass-api-python-wrapper/commit/20c1582c67e892bdefcf215a265f87384829f861)

## 0.0.1 - 2014-09-16

### Fixed

- fix example [`#6`](https://github.com/mvexel/overpass-api-python-wrapper/issues/6)
- Adding debugging (fixes #2) and don't require full QL syntax (fixes #1) [`#2`](https://github.com/mvexel/overpass-api-python-wrapper/issues/2) [`#1`](https://github.com/mvexel/overpass-api-python-wrapper/issues/1)

### Commits

- Initial commit [`b38e4ea`](https://github.com/mvexel/overpass-api-python-wrapper/commit/b38e4ea6b0cfd4482afc1815cf331093ac62e3f8)
- initial commit [`0c2b55f`](https://github.com/mvexel/overpass-api-python-wrapper/commit/0c2b55f176685ce4d06aa72d32d43352f6343382)
- branching retrieving logic into separate function [`6820bfe`](https://github.com/mvexel/overpass-api-python-wrapper/commit/6820bfe34a227ae750a5a974da024fdaf8d7a0ea)
