# CHANGELOG

## [1.1.0] - 2026-22-04
### Added 
- An export button to export the minified file in a destination of the user's choice
- A `.qss` stylesheet file to set styling of the application
- Exporting files defaults to `generated/` directory for ease of use.
    - Maybe change this to a common directory such as `%appdata%/` in future?  

### Changed
- MAJOR updates to the UI, looks much cleaner and more modern now
- Used `assets/styles.qss` to set the styling of the application
- Only logs first 100 characters of minified file to maintain cleanliness in logs


## [1.0.0] - 2026-22-04
### Added
- GUI to use the program
- Logs to track actions
- Buttons to choose a file to minify
### Changed
- Entrypoint changed from command line to running `__main__.py` directly, and using the application
### Deleted
- CLI entrypoint and args

## [BETA] - 2026-22-04
Entrypoint through CLI : `__main__.py`
### Added
- Simple command line functionality
- Called by using command:
    - `python __main__.py {FILE TO MINIFY}`
- Currently supports minification of `.html` and `.json` files.
- Has PyInstaller executable along with a helper batch file `build.bat` to build into exe in future versions (windowed, onefile).