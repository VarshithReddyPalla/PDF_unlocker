# PDF Unlocker

A small Python desktop app for removing PDF password protection using a password you already know. Select or drag in multiple PDFs, enter their shared password, and unlock them locally.

**The app replaces each original PDF with its unlocked copy under the same filename.** It first saves the protected original in a backup folder. Existing backup filenames receive a numbered suffix so earlier backups are preserved.

## Setup

Requires Python 3.10 or newer with Tkinter and a graphical desktop. The dependencies are pinned to the versions used for local verification. Windows is the primary development platform; other platforms have not been manually verified.

From the repository folder on Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe unlock.py
```

On macOS or Linux with a Tk-enabled Python installation:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python unlock.py
```

Tkinter is supplied by your Python installation or operating system, rather than pip. If importing `tkinter` fails, install Tk support for your Python interpreter. The `crypto` extra provides support for AES-encrypted PDFs.

## Usage

1. Enter the password shared by the PDFs you want to process.
2. Review the backup folder, or use **Choose** to select another location.
3. Drop PDFs onto the window, or click the drop area to select files.
4. Confirm replacement of the originals and review the result summary.

The default backup folder is `PDFUnlocker/backups` inside your user home directory. The folder is created when processing files. The selected folder is not remembered between launches.

Unencrypted PDFs are skipped. Incorrect passwords and other failures are reported per file. Files with different passwords should be processed in separate batches. This app does not recover or guess passwords; use it only on documents you own or are authorized to modify.

## File handling and limitations

- PDF processing happens locally; the app does not upload documents or save passwords to a settings file.
- Each unlocked PDF is written to a temporary file before replacing the original. Keep the backups until you have checked the output.
- The app copies PDF pages into a new document. Document-level features such as bookmarks, attachments, forms, metadata, and digital signatures may not be preserved. Do not rely on it to preserve signed documents.
- Large batches run on the UI thread and may make the window temporarily unresponsive.
- PDFs, common backup folders, virtual environments, and common secret files are excluded by `.gitignore`. Files already tracked by Git are not protected by ignore rules.

## Development

Run the automated checks with:

```sh
python -m unittest discover -s tests -v
```

Tests generate temporary PDFs and exercise processing without opening a GUI. GitHub Actions runs them on Windows and Linux. Drag-and-drop and window layout still need a manual desktop check.

Before pushing, review `git status` and `git diff --cached` to ensure no personal documents or credentials are staged. When reporting bugs, include your OS, Python version, and error message; avoid attaching private PDFs or passwords.

## License

Licensed under the [MIT License](LICENSE).
