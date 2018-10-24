# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- `buffering` parameter for Poller class

### Changed
- Poller will return multiple results for line-based channels when there are several lines

### Fixed
- Poller will no longer send empty messages for line-based channels
- Bettercodehub link in README

## 0.1.1 - 2018-10-14
### Added
- License
- Readme
- This changelog
- Channel class
- PipeChannel class
- SocketChannel class
- LineChannel class
- TestChannel class
- Poller class

[Unreleased]: https://github.com/aragaer/channels/compare/v0.1.1...HEAD
