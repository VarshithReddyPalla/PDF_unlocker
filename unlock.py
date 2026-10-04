import os
import shutil
import tempfile
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
from pypdf import PdfReader, PdfWriter


class PDFUnlockerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Unlocker")
        self.root.geometry("450x365")
        self.root.resizable(False, False)

        # Default backup folder
        self.backup_folder = os.path.join(
            os.path.expanduser("~"), "PDFUnlocker", "backups"
        )

        # --------------------------------------------------
        # Title
        # --------------------------------------------------
        title = tk.Label(
            root,
            text="PDF Unlocker",
            font=("Segoe UI", 17, "bold")
        )
        title.pack(pady=(16, 2))

        subtitle = tk.Label(
            root,
            text="Select or drop one or more password-protected PDFs",
            font=("Segoe UI", 9),
            fg="#666666"
        )
        subtitle.pack(pady=(0, 10))

        # --------------------------------------------------
        # Backup folder
        # --------------------------------------------------
        backup_frame = tk.Frame(root)
        backup_frame.pack(fill="x", padx=28, pady=3)

        tk.Label(
            backup_frame,
            text="Backup folder:",
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w")

        folder_row = tk.Frame(backup_frame)
        folder_row.pack(fill="x", pady=3)

        self.backup_label = tk.Label(
            folder_row,
            text=self.backup_folder,
            bg="#f3f3f3",
            fg="#222222",
            anchor="w",
            padx=8,
            font=("Segoe UI", 8)
        )
        self.backup_label.pack(
            side="left",
            fill="x",
            expand=True,
            ipady=5
        )

        tk.Button(
            folder_row,
            text="Choose",
            command=self.choose_backup_folder,
            width=8
        ).pack(side="right", padx=(6, 0))

        # --------------------------------------------------
        # Drag/drop area
        # --------------------------------------------------
        self.drop_area = tk.Label(
            root,
            text="DROP PDFS HERE\n\nor click to select",
            font=("Segoe UI", 11, "bold"),
            fg="#555555",
            bg="#eeeeee",
            relief="ridge",
            bd=2,
            width=40,
            height=6
        )
        self.drop_area.pack(
            padx=28,
            pady=12,
            fill="both"
        )

        self.drop_area.drop_target_register(DND_FILES)
        self.drop_area.dnd_bind("<<Drop>>", self.handle_drop)
        self.drop_area.bind("<Button-1>", self.select_pdfs)

        # --------------------------------------------------
        # Password area
        # --------------------------------------------------
        password_frame = tk.Frame(root)
        password_frame.pack(
            fill="x",
            padx=28,
            pady=(0, 2)
        )

        tk.Label(
            password_frame,
            text="Password:",
            font=("Segoe UI", 9, "bold")
        ).pack(side="left")

        self.password_var = tk.StringVar()

        self.password_entry = tk.Entry(
            password_frame,
            textvariable=self.password_var,
            show="*",
            width=27
        )
        self.password_entry.pack(
            side="left",
            padx=(7, 5)
        )

        self.show_password_var = tk.BooleanVar(value=False)

        tk.Checkbutton(
            password_frame,
            text="Show",
            variable=self.show_password_var,
            command=self.toggle_password
        ).pack(side="left")

        # --------------------------------------------------
        # Status
        # --------------------------------------------------
        status_frame = tk.Frame(root, height=38)
        status_frame.pack(
            fill="x",
            padx=28,
            pady=(10, 8)
        )

        status_frame.pack_propagate(False)

        self.status = tk.Label(
            status_frame,
            text="Ready",
            font=("Segoe UI", 9),
            fg="#444444",
            anchor="center",
            justify="center",
            wraplength=390
        )
        self.status.pack(
            fill="both",
            expand=True
        )

    # ======================================================
    # Toggle password visibility
    # ======================================================
    def toggle_password(self):
        if self.show_password_var.get():
            self.password_entry.config(show="")
        else:
            self.password_entry.config(show="*")

    # ======================================================
    # Choose backup folder
    # ======================================================
    def choose_backup_folder(self):
        folder = filedialog.askdirectory(
            title="Choose backup folder",
            initialdir=self.backup_folder
        )

        if folder:
            self.backup_folder = folder
            os.makedirs(self.backup_folder, exist_ok=True)

            self.backup_label.config(
                text=folder,
                fg="#222222"
            )

    # ======================================================
    # Select multiple PDFs
    # ======================================================
    def select_pdfs(self, event=None):
        files = filedialog.askopenfilenames(
            title="Select PDF files",
            filetypes=[
                ("PDF files", "*.pdf"),
                ("All files", "*.*")
            ]
        )

        if files:
            self.process_pdfs(list(files))

    # ======================================================
    # Handle drag & drop
    # ======================================================
    def handle_drop(self, event):
        files = self.root.tk.splitlist(event.data)

        pdf_files = [
            file_path
            for file_path in files
            if file_path.lower().endswith(".pdf")
        ]

        if not pdf_files:
            messagebox.showerror(
                "Invalid files",
                "Please drop one or more PDF files."
            )
            return

        self.process_pdfs(pdf_files)

    # ======================================================
    # Main processing
    # ======================================================
    def process_pdfs(self, pdf_paths):

        if not pdf_paths:
            return

        # Remove invalid paths
        pdf_paths = [
            path for path in pdf_paths
            if os.path.isfile(path)
        ]

        if not pdf_paths:
            messagebox.showerror(
                "Error",
                "No valid PDF files were selected."
            )
            return

        # --------------------------------------------------
        # Make sure backup folder exists
        # --------------------------------------------------
        try:
            os.makedirs(self.backup_folder, exist_ok=True)
        except Exception as e:
            messagebox.showerror(
                "Backup folder error",
                f"Could not create the backup folder:\n\n{e}"
            )
            return

        # --------------------------------------------------
        # Get password from password box
        # --------------------------------------------------
        password = self.password_var.get()

        if not password:
            messagebox.showwarning(
                "Password required",
                "Please enter the PDF password."
            )
            self.password_entry.focus_set()
            return

        # --------------------------------------------------
        # Confirm operation
        # --------------------------------------------------
        count = len(pdf_paths)

        answer = messagebox.askyesno(
            "Confirm unlock",
            f"You selected {count} PDF"
            f"{'s' if count != 1 else ''}.\n\n"
            "Each original PDF will first be backed up.\n\n"
            "After the backup succeeds, the unlocked PDF will "
            "replace the original file using the SAME filename.\n\n"
            "Continue?"
        )

        if not answer:
            return

        self.status.config(
            text=f"Processing {count} PDF(s)...",
            fg="#555555"
        )
        self.root.update_idletasks()

        successful = []
        failed = []
        already_unlocked = []

        # ==================================================
        # Process each PDF
        # ==================================================
        for index, pdf_path in enumerate(pdf_paths, start=1):

            filename = os.path.basename(pdf_path)

            self.status.config(
                text=f"Processing {index}/{count}: {filename}",
                fg="#555555"
            )
            self.root.update_idletasks()

            try:
                # ------------------------------------------
                # Read PDF
                # ------------------------------------------
                reader = PdfReader(pdf_path)

                # ------------------------------------------
                # Already unlocked
                # ------------------------------------------
                if not reader.is_encrypted:
                    already_unlocked.append(filename)
                    continue

                # ------------------------------------------
                # Try password
                # ------------------------------------------
                decrypt_result = reader.decrypt(password)

                if not decrypt_result:
                    raise ValueError(
                        "Incorrect password."
                    )

                # ------------------------------------------
                # Create backup
                # ------------------------------------------
                backup_path = self.get_backup_path(filename)

                shutil.copy2(
                    pdf_path,
                    backup_path
                )

                # ------------------------------------------
                # Create unlocked PDF in a temporary file
                #
                # IMPORTANT:
                # We don't overwrite the original until
                # the new PDF has been successfully written.
                # ------------------------------------------
                original_folder = os.path.dirname(pdf_path)

                fd, temp_path = tempfile.mkstemp(
                    suffix=".pdf",
                    dir=original_folder
                )

                os.close(fd)

                try:
                    writer = PdfWriter()

                    for page in reader.pages:
                        writer.add_page(page)

                    with open(temp_path, "wb") as output_file:
                        writer.write(output_file)

                    # --------------------------------------
                    # Replace original with unlocked PDF
                    # --------------------------------------
                    os.replace(
                        temp_path,
                        pdf_path
                    )

                    temp_path = None

                finally:
                    # Clean up temporary file if something
                    # went wrong before replacement.
                    if temp_path and os.path.exists(temp_path):
                        try:
                            os.remove(temp_path)
                        except OSError:
                            pass

                successful.append(filename)

            except Exception as e:
                failed.append(
                    f"{filename}\n   {str(e)}"
                )

        # ==================================================
        # Final result
        # ==================================================
        success_count = len(successful)
        failed_count = len(failed)
        already_count = len(already_unlocked)

        if success_count > 0:
            self.status.config(
                text=f"Done - {success_count} PDF(s) unlocked.",
                fg="#008000"
            )
        elif failed_count > 0:
            self.status.config(
                text="Processing completed with errors.",
                fg="#cc0000"
            )
        else:
            self.status.config(
                text="Nothing needed unlocking.",
                fg="#555555"
            )

        # --------------------------------------------------
        # Build result message
        # --------------------------------------------------
        result_message = ""

        if successful:
            result_message += (
                f"Successfully unlocked: {success_count}\n\n"
            )

            result_message += (
                "The unlocked PDFs replaced the original files "
                "using the same filenames.\n\n"
            )

            result_message += (
                "Backups were saved to:\n"
                f"{self.backup_folder}\n"
            )

        if already_unlocked:
            result_message += (
                f"\nAlready unlocked: {already_count}\n"
            )

            for filename in already_unlocked:
                result_message += f"• {filename}\n"

        if failed:
            result_message += (
                f"\nFailed: {failed_count}\n"
            )

            for error in failed:
                result_message += f"\n• {error}\n"

        # --------------------------------------------------
        # Show final result
        # --------------------------------------------------
        if failed_count > 0:
            messagebox.showwarning(
                "Processing completed",
                result_message
            )
        else:
            messagebox.showinfo(
                "Processing completed",
                result_message
            )

    # ======================================================
    # Get unique backup path
    # ======================================================
    def get_backup_path(self, filename):

        backup_path = os.path.join(
            self.backup_folder,
            filename
        )

        # Don't overwrite an existing backup.
        if not os.path.exists(backup_path):
            return backup_path

        base, extension = os.path.splitext(filename)

        counter = 1

        while True:

            backup_path = os.path.join(
                self.backup_folder,
                f"{base}_backup_{counter}{extension}"
            )

            if not os.path.exists(backup_path):
                return backup_path

            counter += 1


# ==========================================================
# Start application
# ==========================================================

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = PDFUnlockerApp(root)
    root.mainloop()
