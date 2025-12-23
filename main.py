from PIL import Image
# import PIL
import tkinter as tk
from tkinter import ttk
import os
import threading

class Output:

    def __init__(self, filename: str, input_folder: str, output_folder: str, watermark, position: str):
        self.filename: str = filename
        self.output_folder: str = output_folder
        self.input_folder: str = input_folder
        self.watermark = watermark
        self.position: str = position

    def Save(self) -> bool:
        if not self.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            return False
        
        img_path: str = os.path.join(self.input_folder, self.filename)

        base_image = Image.open(img_path).convert("RGBA")

        x, y = self.selectPosition(base_image)

        # paste watermark
        base_image.paste(self.watermark, (x, y), self.watermark)
        base_image = base_image.convert("RGB")

        # save
        path = os.path.join(self.output_folder, self.filename)
        base_image.save(os.path.join(path))

        return True

    def selectPosition(self, base_image) -> tuple:
        x: int = 0
        y: int = 0
        if self.position == 'bottom_right':
            x = base_image.width - self.watermark.width - 10
            y = base_image.height - self.watermark.height - 10
        elif self.position == 'top_right':
            x = base_image.width - self.watermark.width - 10
            y = 10
        elif self.position == 'top_left':
            x = 10
            y = 10
        elif self.position == 'bottom_left':
            x = 10
            y = base_image.height - self.watermark.height - 10
        elif self.position == 'auto':
            x, y = self.AutoPosition(base_image)
        return x, y
    
    def AutoPosition(self, baseImage) -> tuple:
        x: int = 0
        y: int = 0

        return x, y
        

class Watermark:

    def __init__(self, imgpath: str, opacity: int, scale: float):
        self.imgpath: str = imgpath
        self.opacity: int = opacity
        self.scale: float = scale
        self.filenotfound: bool = False

        try:
            self.watermark = Image.open(self.imgpath).convert("RGBA")
        except FileNotFoundError:
            self.filenotfound = True

    def newWatermark(self):
        nwidth: int = int(self.watermark.width * self.scale)
        nheight: int = int(self.watermark.height * self.scale)
        newsize: tuple = (nwidth, nheight)
        self.watermark = self.watermark.resize(newsize, Image.Resampling.LANCZOS)

        watermarkmask = self.watermark.split()[3].point(lambda i: i * self.opacity / 255)
        self.watermark.putalpha(watermarkmask)

    def checkImage(self):
        pass

class Desktop:

    posMenu: dict = {'Top Left': 'top_left',
                 'Top Right': 'top_right',
                 'Bottom Left': 'bottom_left',
                 'Bottom Right': 'bottom_right',
                 'Auto': 'auto'
                }

    def __init__(self):
        self.root: tk.Tk = tk.Tk()
        self.root.title("Yanji Watermark")
        self.root.geometry("400x300")

        self.input_folder: tk.Entry = self.usrInput("Input path")
        self.output_folder: tk.Entry = self.usrInput("Output path")
        self.watermark_path: tk.Entry = self.usrInput("Watermark path")
        self.opacity: int = 255
        self.scale: tk.Entry = self.usrInput("Watermark scale(0-10)", '3.0')
        self.position: ttk.Combobox = self.positionMenu("Select Position")
        self.nbutton()

        self.interup: bool = False

        self.root.mainloop()

    def usrInput(self, text, value=None) -> tk.Entry:
        frame: tk.Frame = tk.Frame(self.root)
        label: tk.Label = tk.Label(frame, text=text)
        entry: tk.Entry = tk.Entry(frame, width=20)
        if value:
            entry.insert(0, value)

        # pack this shit
        frame.pack(pady=10, padx=10, fill=tk.X)
        label.pack(side=tk.LEFT)
        entry.pack(fill=tk.X, expand=True)

        return entry
    
    def positionMenu(self, text) -> ttk.Combobox:
        frame: tk.Frame = tk.Frame(self.root)
        label: tk.Label = tk.Label(frame, text=text)
        cb: ttk.Combobox = ttk.Combobox(frame, values=list(self.posMenu))
        cb.set("Top Left")

        frame.pack(pady=10, padx=10, fill=tk.X)
        label.pack(side=tk.LEFT)
        cb.pack(fill=tk.X)

        return cb
    
    def nbutton(self):
        frame: tk.Frame = tk.Frame(self.root)
        btn: tk.Button = tk.Button(frame, text="Proceed", command=self.processSaving)
        cbtn: tk.Button = tk.Button(frame, text='Clear', command=self.clear)

        # pack this shit
        frame.pack(pady=10, padx=10, fill=tk.X)
        btn.pack(side=tk.LEFT, padx=5)
        cbtn.pack(side=tk.LEFT, padx=5)

    def processSaving(self):
        self.interup = False
        thread = threading.Thread(target=self.save)
        thread.start()

    def save(self):
        self.nWindow()
        self.progress['value'] = 0
        self.progresslabel.config(text='Saving...')
        count: int = 0

        os.makedirs(self.output_folder.get(), exist_ok=True)

        # check if scale is not numeric
        try:
            float(self.scale.get())
        except ValueError:
            self.progresslabel.config(text="Watermark scale value is invalid")
            return

        watermark: Watermark = Watermark(self.watermark_path.get(), self.opacity, float(self.scale.get()))
        if watermark.filenotfound:
            self.progresslabel.config(text="Watermark Image Not Found")
            return
        watermark.newWatermark()

        _dir: list[str] = []
        try:
            _dir = os.listdir(self.input_folder.get())
        except FileNotFoundError:
            self.progresslabel.config(text=f"Path Not Found {self.input_folder.get()}")
            return

        for filename in _dir:
            if self.interup:
                self.interup = False
                break
            
            # new output file
            nOutput: Output = Output(filename, self.input_folder.get(), self.output_folder.get(), watermark.watermark, self.posMenu[self.position.get()])
            
            # save the new image
            if not nOutput.Save():
                self.progresslabel.config(text=f"Invalid image file {filename}")
                return
            count+=1
            self.progress['value'] = (count / len(_dir)) * 100
            self.progresslabel.config(text=f"Saving {filename}")
            self.root.update_idletasks()

        self.progresslabel.config(text="Done")

    def nWindow(self):
        self.nwin: tk.Toplevel = tk.Toplevel(self.root)
        self.nwin.title("Saving...")
        self.nwin.geometry("250x150")

        self.progresslabel: tk.Label = tk.Label(self.nwin, text='Saving...')

        self.progress: ttk.Progressbar = ttk.Progressbar(
            self.nwin,
            orient="horizontal",
            length=250,
            mode="determinate",
            maximum=100
        )

        self.progresslabel.pack(pady=20)
        self.progress.pack(pady=20)

        self.nwin.protocol("WM_DELETE_WINDOW", self.onClose)

    def onClose(self):
        self.interup = True
        self.nwin.destroy()

    def clear(self):
        self.input_folder.delete(0, tk.END)
        self.output_folder.delete(0, tk.END)
        self.watermark_path.delete(0, tk.END)

if __name__=='__main__':
    Desktop()
