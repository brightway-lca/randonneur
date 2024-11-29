# randonneur Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

* Add `read_excel_template`
* Better follow [Datapackage standard for `contributors`](https://datapackage.org/standard/data-package/#contributors).

## [0.5] - 2024-09-11

* Add node creation and deletion
* Add exchange creation and deletion
* Change data format for creation from `targets` to singular `target`. Not a breaking change as creation was unsupported previously.

## [0.4] - 2024-09-04

* Add `create_excel_template` function
* Add all [SPDX](https://spdx.org/licenses/) licenses

## [0.3] - 2024-09-02

* Allow optional propagation of extra transformation attributes

### [0.2.2] - 2024-09-01

* Fix validation of contributors as list

### [0.2.1] - 2024-09-01

* Refactor data validation into a separate function

## [0.2.0] - 2024-08-31

* Update `FlexibleLookupDict` to allow multiple input pairs if identical results are produced
* Validate `Datapackage` metadata with `pydantic`
* Refactor config arguments out to `pydantic` class

## [0.1.0] - 2024-08-14

Initial first working release
