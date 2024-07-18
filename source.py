import tkinter as tk
from tkinter import messagebox
import requests
import threading
import time
from tqdm import tqdm

class DownloadTool:
    def __init__(self, root):
        self.root = root
        self.root.title("DownloaderX by Mustafa IP")
        self.root.configure(bg='#2e2e2e')
        
        self.stop_event = threading.Event()
        self.resume_event = threading.Event()
        self.speed_option = tk.StringVar(value="full")
        
        self.url_label = tk.Label(root, text="Download URL:", fg="white", bg="#2e2e2e", font=("Helvetica", 12))
        self.url_label.grid(row=0, column=0, padx=10, pady=10)
        
        self.url_entry = tk.Entry(root, width=50, bg='#3c3c3c', fg='white', insertbackground='white', font=("Helvetica", 12))
        self.url_entry.grid(row=0, column=1, padx=10, pady=10)
        
        self.download_button = tk.Button(root, text="Download", command=self.start_download, fg="white", bg="#1a73e8", font=("Helvetica", 12))
        self.download_button.grid(row=0, column=2, padx=10, pady=10)
        
        self.stop_button = tk.Button(root, text="Stop", command=self.stop_download, fg="white", bg="#ea4335", font=("Helvetica", 12))
        self.stop_button.grid(row=1, column=0, padx=10, pady=10)
        
        self.resume_button = tk.Button(root, text="Resume", command=self.resume_download, fg="white", bg="#34a853", font=("Helvetica", 12))
        self.resume_button.grid(row=1, column=1, padx=10, pady=10)
        
        self.speed_label = tk.Label(root, text="Download Speed:", fg="white", bg="#2e2e2e", font=("Helvetica", 12))
        self.speed_label.grid(row=2, column=0, padx=10, pady=10)
        
        self.full_speed_radiobutton = tk.Radiobutton(root, text="Full Speed", variable=self.speed_option, value="full", fg="white", bg="#2e2e2e", font=("Helvetica", 12), selectcolor='#2e2e2e')
        self.full_speed_radiobutton.grid(row=2, column=1, padx=10, pady=10)
        
        self.half_speed_radiobutton = tk.Radiobutton(root, text="Half Speed", variable=self.speed_option, value="half", fg="white", bg="#2e2e2e", font=("Helvetica", 12), selectcolor='#2e2e2e')
        self.half_speed_radiobutton.grid(row=2, column=2, padx=10, pady=10)
        
        self.progress_label = tk.Label(root, text="Progress: 0%", fg="white", bg="#2e2e2e", font=("Helvetica", 12))
        self.progress_label.grid(row=3, column=0, columnspan=3, padx=10, pady=10)
        
        self.speed_display_label = tk.Label(root, text="Speed: 0 KB/s", fg="white", bg="#2e2e2e", font=("Helvetica", 12))
        self.speed_display_label.grid(row=4, column=0, columnspan=3, padx=10, pady=10)
        
        self.time_label = tk.Label(root, text="Time Remaining: 0h 0m", fg="white", bg="#2e2e2e", font=("Helvetica", 12))
        self.time_label.grid(row=5, column=0, columnspan=3, padx=10, pady=10)
        
        self.size_label = tk.Label(root, text="File Size: 0 MB", fg="white", bg="#2e2e2e", font=("Helvetica", 12))
        self.size_label.grid(row=6, column=0, columnspan=3, padx=10, pady=10)
        
        self.downloaded_label = tk.Label(root, text="Downloaded: 0 MB", fg="white", bg="#2e2e2e", font=("Helvetica", 12))
        self.downloaded_label.grid(row=7, column=0, columnspan=3, padx=10, pady=10)

    def start_download(self):
        self.stop_event.clear()
        self.resume_event.set()
        url = self.url_entry.get()
        if not url:
            messagebox.showerror("Error", "Please enter a URL")
            return
        
        self.thread = threading.Thread(target=self.download_file, args=(url,))
        self.thread.start()

    def stop_download(self):
        self.stop_event.set()
        
    def resume_download(self):
        self.stop_event.clear()
        self.resume_event.set()
        
    def download_file(self, url):
        local_filename = url.split('/')[-1]
        start_time = time.time()
        
        with requests.get(url, stream=True) as r:
            total_size = int(r.headers.get('content-length', 0))
            block_size = 1024
            progress = 0
            with open(local_filename, 'wb') as f:
                with tqdm(total=total_size, unit='B', unit_scale=True, desc=local_filename, initial=progress, ascii=True) as pbar:
                    for data in r.iter_content(block_size):
                        self.resume_event.wait()
                        if self.stop_event.is_set():
                            break
                        f.write(data)
                        progress += len(data)
                        pbar.update(len(data))
                        elapsed_time = time.time() - start_time
                        speed = progress / elapsed_time / 1024
                        time_remaining = (total_size - progress) / speed / 1024
                        
                        
                        if self.speed_option.get() == "half":
                            time.sleep(0.5)
                        
                        self.update_progress(progress, total_size, speed, time_remaining)

    def update_progress(self, progress, total_size, speed, time_remaining):
        percent = (progress / total_size) * 100
        time_remaining_h = int(time_remaining // 60)
        time_remaining_m = int(time_remaining % 60)
        downloaded_mb = progress / (1024 * 1024)
        total_size_mb = total_size / (1024 * 1024)
        self.progress_label.config(text=f"Progress: {percent:.2f}%")
        self.speed_display_label.config(text=f"Speed: {speed:.2f} KB/s")
        self.time_label.config(text=f"Time Remaining: {time_remaining_h}h {time_remaining_m}m")
        self.size_label.config(text=f"File Size: {total_size_mb:.2f} MB")
        self.downloaded_label.config(text=f"Downloaded: {downloaded_mb:.2f} MB")
        self.root.update_idletasks()

if __name__ == "__main__":
    root = tk.Tk()
    app = DownloadTool(root)
    root.mainloop()
