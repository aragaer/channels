# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.3] - 2024-05-27
### Changed
- Using nose2 instead of nose now

### Fixed
- No data was delivered when PipeChannel was closed before data was read

## [0.2.2] - 2018-11-05
### Fixed
- Poller now registers server for POLLIN only.
- Poller unregisters the client channel when it is closed

## [0.2.1] - 2018-11-05
### Fixed
- Fixed the error when poller tried to accept an incoming connection when the event was not POLLIN

## [0.2.0] - 2018-10-25
### Added
- `buffering` parameter for Poller class
- `buffering` parameter for channels

### Changed
- Poller will return multiple results for line-based channels when there are several lines

### Removed
- LineChannel class

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

[Unreleased]: https://github.com/aragaer/channels/compare/v0.2.2...HEAD
[0.2.2]: https://github.com/aragaer/channels/compare/v0.2.1...v0.2.2
[0.2.1]: https://github.com/aragaer/channels/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/aragaer/channels/compare/v0.1.1...v0.2.0
