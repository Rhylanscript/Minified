# CHANGELOG

## [1.2.4] - 2026-23-04
### Changed
- User now has the option to choose filename when exporting singular files.

### Fixed
- Clicking export now opens to `generated/` by default
    - Maybe change to a common folder like `%localappdata%/` or `Downloads/` in future?
<br>

## [1.2.3] - 2026-23-04
### Added 
- Logs now show the time at which they were sent
- Modified default window size
<br>

## [1.2.2] - 2026-22-04
### Changed
- Moved minification function in `ui/main_window.py` to `core/worker.py`
- Minification function now runs on a Thread in `ui/main_window.py` as to not freeze window while active
<br>

## [1.2.1] - 2026-22-04
### Added
- File size overview (original size vs minified size & reduction %)
<br>

## [1.2.0] - 2026-22-04
### Added 
- Drag and drop functionality (files can be dropped onto the app)
- Added multi-file support

### Changed
- Minor UI refinements
    - Fixed scrollbar of logbox
    - Improved UI of logbox
    - More user feedback on buttons (enabled / disabled states)

### Fixed
- Scroll bar design in UI (previously was unformatted and looked ugly)
- Issues when displaying selected file extension and exporting
<br>

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
<br>

## [1.0.0] - 2026-22-04
### Added
- GUI to use the program
- Logs to track actions
- Buttons to choose a file to minify
### Changed
- Entrypoint changed from command line to running `__main__.py` directly, and using the application
### Deleted
- CLI entrypoint and args
<br>

## [BETA] - 2026-22-04
Entrypoint through CLI : `__main__.py`
### Added
- Simple command line functionality
- Called by using command:
    - `python __main__.py {FILE TO MINIFY}`
- Currently supports minification of `.html` and `.json` files.
- Has PyInstaller executable along with a helper batch file `build.bat` to build into exe in future versions (windowed, onefile).