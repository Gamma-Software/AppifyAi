# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.5.1] - 2023-07-21

### Fixed

- make sure the last code is at least the init code
- get last code generated instead of the code in the current sandbox file

## [1.5.0] - 2023-07-21

### Modified

- Push tag now commit and push the bump of version, then push tag

### Fixed

- Fixed the bug where the signup was not done for new users
- Now on signup the message is better looking and well placed

## [1.4.0] - 2023-07-21

Change ChatbotX name to AppifyAi

### Added

- demo on face detection
- add pylint workflow
- Catch phrase at first
- secrets for tries
- Now you can quickly login and signup when enter is pressed
- About page

### Fixed

- Sandbox was not recreated after a syntax error
- Code history to undo

## [1.3.0] - 2023-07-19

### Added

- Push tag script
- tasks
- Ideas to develop in readme

### Modified

- Replaced the constitutional chain by a function to analyse code
- Move the shell scripts to scripts folder

### Fixed

- the undo was not removing the last discussion
- At first start the chat was invisible
- The explanation was not saved in the database

## [1.2.0] - 2023-07-18

### Modified

- Add expander to code generated
- Apply the code only when the generated page is requested by the user

## [1.1.0] - 2023-07-16

### Added

- Refactoring of sandboxe managment (in order to garanty the sandboxe custering)
- Better handle caching

## [1.0.0] - 2023-07-15

### Added

- Make the streamlit application work
- The chabot is now able to answer to the user
- The chatbot is now able to generate the code and apply it instantly
- The streamlit generated app is now downloadable

[Unreleased]: https://github.com/Gamma-Software/AppifyAi/compare/v1.5.1...HEAD
[1.5.1]: https://github.com/Gamma-Software/AppifyAi/compare/v1.5.0...v1.5.1
[1.5.0]: https://github.com/Gamma-Software/AppifyAi/compare/v1.4.0...v1.5.0
[1.4.0]: https://github.com/Gamma-Software/AppifyAi/compare/v1.3.0...v1.4.0
[1.3.0]: https://github.com/Gamma-Software/AppifyAi/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/Gamma-Software/AppifyAi/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/Gamma-Software/AppifyAi/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/Gamma-Software/AppifyAi/releases/tag/v1.0.0