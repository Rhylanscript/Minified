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

It currently supports multi-files, and drag and dropping, as well as having a comprehensive log system to notify the user of processes and an appealing UI, with toggleable theming for light and dark modes!

## How to Use
To use it, simply run `build.bat` and run the exe that is generated in `build/`. To upload files to be minified, either drag them onto the application, or use the __open__ button, and select the files you want. Then click the __minify__ button which will show a short preview of your file, and export it to a location of your choice!

## Notes
The JavaScript Minifier uses `esbuild` for safest results. It is recommended to run:
<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`npm install -g esbuild`<br>
for the best (and most consistent) results.

## Feedback
Any feedback is much appreciated! Thank you!