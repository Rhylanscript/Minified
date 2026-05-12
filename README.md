# MINIFIED
A Minifying tool for __LOTS__ of filetypes
By Rhylan M

## Overview
Minified is a useful application which can be used to minify multiple common filetypes, some of which include:
- HTML
- JSON
- CSS
- JavaScript
- SVG/XML
- LUA

It currently supports multi-files, and drag and dropping, as well as having a comprehensive log system to notify the user of processes and an appealing UI, with toggleable theming for light and dark modes!

## How to Use
To use it, simply run `bootstrap.bat` to install dependencies, and then run `build.bat` to generate an exe in `dist/`. 

To upload files to be minified, either drag them onto the application, or use the __open__ button, and select the files you want. Then click the __minify__ button which will show a short preview of your file, and export it using the __export__ button to make it at a location of your choice!

## Notes
The JavaScript Minifier uses `esbuild` for safest results. Please ensure you have node.js installed from the official website [here.][nodejs]

Minified uses python pip packages. If you don't already see [this website][pip] to install pip.
## Feedback
Any feedback is much appreciated! Thank you!

<!-- Reference links -->
[nodejs]: https://nodejs.org/en
[pip]: https://pypi.org/project/pip/