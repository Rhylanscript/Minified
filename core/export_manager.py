# core/export_manager.py

"""
Manages export processes in the application.

Houses the ExportManager class, which controls export directories,
export filenames, exporting of files, tracking last export dir and
more.
"""

import os

from utils.util import get_filename

from PyQt6.QtWidgets import QFileDialog

class ExportManager:
    """
    Handles processes which involve exporting of files.

    This includes:
    - creating export dirs
    - generating output filenames
    - exporting one / many files 
    - tracking last export dir
    """
    def __init__(self) -> None:
        self.last_export_dir: str | None = None

    def get_default_export_dir(self) -> str:
        """
        Method to get the default export directory.

        Returns:
            The default export dir.
        """
        directory = os.path.join(os.getcwd(), "generated")
        os.makedirs(directory, exist_ok=True)
        return directory

    def build_output_name(self, path: str) -> str:
        """
        Method to create the output name given the original. Splices 
        the name at the extension and inserts `.min.` between the file
        name and extension.

        Args:
            path: Path to the file.
        
        Returns:
            The new minified filename.
        """
        name = get_filename(path)
        base, ext = os.path.splitext(name)

        return f"{base}.min{ext}"
    
    def export(self, output_path: str, content: str) -> None:
        """
        Write the provided content to a file located at the provided
        path and update last export directory.

        Args:
            output_path: The path at which to write the file
            content: The content of the minified file
        """
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)

        self.last_export_dir = os.path.dirname(output_path)

    def export_files(
            self,
            parent,
            results: list[tuple[str, str]],
            output
        ) -> str | None:
        """
        Export one or multiple minified files.

        Args:
            parent: Parent widget for dialogs
            results: Minified file results
            output: Log output widget

        Returns:
            Export directory or None if cancelled.
        """

        default_dir = self.get_default_export_dir()

        if len(results) == 1:
            path, content = results[0]

            default_name = self.build_output_name(path)
            save_path, _ = QFileDialog.getSaveFileName(parent,
                "Save Minified File",
                os.path.join(default_dir, default_name)
            )
            if not save_path: return None

            self.export(save_path, content)
            output.success(
                f"Exported: {get_filename(save_path)}",
                link=save_path
            )

            return os.path.dirname(save_path)
        
        # multi file exporting
        folder = QFileDialog.getExistingDirectory(
            parent,
            "Select Output Folder",
            default_dir
        )
        if not folder: return None

        for path, content in results:
            try:
                new_name = self.build_output_name(path)
                output_path = os.path.join(folder, new_name)

                self.export(output_path, content)
                output.success(
                    f"Exported: {new_name}",
                    link=save_path
                )

            except Exception as e:
                output.error(f"Export failed for {path}: {str(e)}")

        return folder