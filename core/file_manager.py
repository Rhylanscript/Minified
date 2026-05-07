# core/file_manager.py

"""
Manages files in the application.

Houses the FileManager class which adds, removes, updates,
and does more operations with files.
"""

from utils.util import get_filename

class FileManager:
    """
    Class for managing files used in MainWindow.

    Has multiple helper methods to help with the management of
    files being used by the application.
    """
    def __init__(self) -> None:
        self.files: list[str] = []
        self.on_change = None # callback hook that MainWindow will use

    def set_files(self, files: list[str]) -> None:
        """
        Set files to a given value provided.

        Args:
            files: A list of file paths
        """
        self.files = files or []
        if self.on_change: self.on_change(self.files)

    def get_files(self) -> list[str]:
        """
        Getter for files in the manager.

        Returns:
            Files currently in FileManager.
        """
        return self.files

    def add_files(self, files: list[str]) -> None:
        """
        Add files to the file manager.

        Args:
            files: A list of file paths
        """
        self.set_files(files)

    def clear(self) -> None:
        """Clear the file manager of stored files."""
        self.set_files([])

    def has_files(self) -> bool:
        """
        Simple function to check if the file manager currently is
        storing files.

        Returns:
            True if the filemanager has files, False if not.
        """
        return len(self.files) > 0
    
    def get_names(self) -> list[str]:
        """
        Helper function to get a list of file names currently
        stored in the filemanager.

        Returns:
            A list of filenames currently in the filemanager.
        """
        return [get_filename(f) for f in self.files]