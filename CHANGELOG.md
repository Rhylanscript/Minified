# CHANGELOG

## [1.4.0] - 2026-11-05
### Added
- Multiple minifiers for new filetypes including:
    - CSS minifier
    - JavaScript minifier (use esbuild) for best results
    - SVG minifier
    - XML minifier

## [1.3.7] - 2026-11-05
### Fixed
- Anchor colour in the logbox is now more visible for light mode

## [1.3.6] - 2026-11-05
### Fixed
- Application remembers theming of last session via `QSettings`

## [1.3.5] - 2026-11-05
### Changed
- Moved all logic regarding the sidebar from `main_window.py` to `sidebar.py`

## [1.3.4] - 2026-07-05
### Added
- Managers to handle backend tasks in `MainWindow`
- `ThemeToggle` custom widget to track theming

### Changed
- Most minification / export / file management logic is done via managers in `core/` rather than in `MainWindow` now.
- Moved theme control to a custom widget `ThemeToggle` to increase simplicity in `MainWindow`

### Deleted
- Unecessary old methods from `MainWindow`

## [1.3.3] - 2026-07-05
### Added
- The `ui/widgets/` folder to move specialised widget logic out of `MainWindow`

### Changed
- Refactored the logic for the logs and the progress widget to their own classes, which are then implemented in MainWindow.
- Moved most initialisation logic in `MainWindow` to separate methods to clean up logic

## [1.3.2] - 2026-07-05
### Added
- `__init__.py` files for every folder to show docstring when hovered in vscode (useful change ok)
- Added more configurations in `.vscode/`
- Better documentation to like EVERY FILE IN THE PROJECT
    - Every class, function, method and file has docstrings for happy

### Changed
- Slightly modified entrypoint to use a `main()` function

## [1.3.1] - 2026-07-05
### Added
- Toggleable theming (now has light mode with an extra button to switch between the two)
- Added folder `assets/themes/` for theming .qss files
    - Hopefully support for custom themes will be added in future
- Added `.vscode/` folder for configurations.

### Changed
- Refactored `styles.qss` from `assets/` to `assets/styles/`
- Changed style loader to support multiple .qss files to allow for theming

### Fixed
- Issues with log text colours not formatting properly

## [1.3.0] - 2026-06-05
### Added
- Split the GUI into a sidebar and content section for organisation

### Changed
- Complete reorganisation of the gui to keep action buttons in a sidebar for easy access
- Progress bar shows underneath the current file label and above logs
- When not actively minifying, progress bar is replaced with a placeholder label

### Fixed
- Progress bar now doesnt snap other widgets when in use
- Percentage text for progress bar now is properly placed on the right of the bar, in alignment with the bar
- Minor fixes to log messages for maximum clarity

## [1.2.8] - 2026-05-05
### Added
- A progress bar that shows the progress of file minification so far
- A separate file for the toast class so it can be used in more cases
    - Currently used to open export folder 

### Changed 
- Minor UI changes
- HTML minifier now also supports `.htm` files

## [1.2.7] - 2026-26-04
### Changed
- Improved the open export folder button system a lot by showing a toast instead of a static button on the GUI
- Changed the styling of the new toast

### Deleted
- Old GUI open export folder butten

## [1.2.6] - 2026-25-04
### Added 
- Coloured text to log message types to improve ui

### Fixed
- Automatically added prefixes and colour formatting to log messages via functions in the `MainWindow` class, `error()`, `warn()`, `success()`, `info()`
- Improved error handling for minification of unsupported types, warns user instead of showing unreadable error

## [1.2.5] - 2026-25-04
### Added
- Exports now show links to file in logs
- Open export folder button opens the folder of the most recent export

### Changed
- Changed logs widget from `QPlainTextWidget` to `QTextBrowser` for more functionality

### Fixed
- Error where exports wouldn't load properly

## [1.2.4] - 2026-23-04
### Changed
- User now has the option to choose filename when exporting singular files.

### Fixed
- Clicking export now opens to `generated/` by default
    - Maybe change to a common folder like `%localappdata%/` or `Downloads/` in future?

## [1.2.3] - 2026-23-04
### Added 
- Logs now show the time at which they were sent
- Modified default window size

## [1.2.2] - 2026-22-04
### Changed
- Moved minification function in `ui/main_window.py` to `core/worker.py`
- Minification function now runs on a Thread in `ui/main_window.py` as to not freeze window while active

## [1.2.1] - 2026-22-04
### Added
- File size overview (original size vs minified size & reduction %)

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