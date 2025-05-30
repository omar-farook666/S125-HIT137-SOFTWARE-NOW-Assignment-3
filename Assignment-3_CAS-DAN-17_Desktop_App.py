import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageTk
import cv2


class ImageCropApp:
    def __init__(self):
        self.original_image_cv = None
        self.current_image_cv = None
        self.cropped_image_cv = None

    def load_image(self,img_path):
        try:
            img = cv2.imread(img_path)
            if img is None:
                raise ValueError("Image cannot be loaded.")
            self.original_image_cv = img
            self.current_image_cv = img.copy()
            self.cropped_image_cv = None
            return True

        except Exception as error:
            messagebox.showerror("Error", f"Failed to load image: {error}")
            return False


    def crop(self, x1, y1, x2, y2):
        if self.current_image_cv is not None:
            # Ensure coordinates are within image bounds
            height, width = self.current_image_cv.shape[:2]
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(width, x2), min(height, y2)

            # Ensure valid crop rectangle (x1 < x2 and y1 < y2)
            if x1 < x2 and y1 < y2:
                self.cropped_image_cv = self.current_image_cv[y1:y2, x1:x2]
                return self.cropped_image_cv
        return None

    def resize(self, scale_factor):
        if self.cropped_image_cv is not None:
            height, width = self.cropped_image_cv.shape[:2]
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            if new_width > 0 and new_height > 0:  # Avoid zero dimensions
                resized_image = cv2.resize(self.cropped_image_cv, (new_width, new_height),
                                           interpolation=cv2.INTER_AREA)
                return resized_image
        return None

    def display_img(self, cv_image):
        if cv_image is None:
            return None
        # Convert BGR to RGB
        rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
        # Convert to PIL Image
        pil_image = Image.fromarray(rgb_image)
        return ImageTk.PhotoImage(pil_image)

    def save_img(self, image_to_save, save_path):

        if image_to_save is not None:
            try:
                cv2.imwrite(save_path, image_to_save)
                messagebox.showinfo("Success", "Image saved successfully!")
                return True
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save image: {e}")
                return False
        return False

class ImageViewer:
    def __init__(self, parent_frame, width, height, image_processor):
        self.canvas = tk.Canvas(parent_frame, width=width, height=height, bg="#F0F0F0", relief="sunken", borderwidth=2)
        self.canvas.pack(side=tk.LEFT, padx=10, pady=10, expand=True, fill=tk.BOTH)

        self.image_processor = image_processor
        self.tk_image = None
        self.display_image_cv = None


        self.x = None
        self.y = None
        self.box_id = None
        self.crop_enable = False
        self.crop_complete = None

        self.canvas.bind("<Button-1>", self.mouse_click)
        self.canvas.bind("<B1-Motion>", self.mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.mouse_up)


    def set_crop_complete(self, clicked):
        self.crop_complete = clicked

    def set_crop_enable(self):
        self.crop_enable = True

    def set_crop_disable(self):
        self.crop_enable = False
        self._clear_rectangle()

    def display_image(self, cv_img):
        self.display_image_cv = cv_img

        if cv_img is None:
            return

        h, w = cv_img.shape[:2]
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()


        if w > canvas_width or h > canvas_height:
            scale_w = canvas_width / w
            scale_h = canvas_height / h
            scale_factor = min(scale_w, scale_h)
            display_w = int(w * scale_factor)
            display_h = int(h * scale_factor)
            resized_for_display = cv2.resize(cv_img, (display_w, display_h), interpolation=cv2.INTER_AREA)
        else:
            resized_for_display = cv_img

        self.tk_image = self.image_processor.display_img(resized_for_display)
        if self.tk_image:

            x = (canvas_width - resized_for_display.shape[1]) / 2
            y = (canvas_height - resized_for_display.shape[0]) / 2
            self.canvas.create_image(x, y, anchor=tk.NW, image=self.tk_image)
            self.canvas.image = self.tk_image

    def _clear_rectangle(self):
        if self.box_id:
            self.canvas.delete(self.box_id)
            self.box_id = None

    def mouse_click(self, event):
        if self.crop_enable and self.display_image_cv is not None:
            self.start_x = event.x
            self.start_y = event.y
            self._clear_rectangle()
            self.box_id = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y,
                                                         outline="red", width=2, dash=(5, 2))

    def mouse_drag(self, event):
        if self.crop_enable and self.start_x is not None:
            self.canvas.coords(self.box_id, self.start_x, self.start_y, event.x, event.y)

    def mouse_up(self, event):
        if self.crop_enable and self.start_x is not None and self.display_image_cv is not None:
            end_x, end_y = event.x, event.y

            h_disp, w_disp = self.display_image_cv.shape[:2]
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()

            scale_w_canvas = canvas_width / w_disp
            scale_h_canvas = canvas_height / h_disp
            scale_factor_canvas = min(scale_w_canvas, scale_h_canvas)


            actual_display_w = int(w_disp * scale_factor_canvas)
            actual_display_h = int(h_disp * scale_factor_canvas)
            offset_x = (canvas_width - actual_display_w) / 2
            offset_y = (canvas_height - actual_display_h) / 2


            img_x1 = int((min(self.start_x, end_x) - offset_x) / scale_factor_canvas)
            img_y1 = int((min(self.start_y, end_y) - offset_y) / scale_factor_canvas)
            img_x2 = int((max(self.start_x, end_x) - offset_x) / scale_factor_canvas)
            img_y2 = int((max(self.start_y, end_y) - offset_y) / scale_factor_canvas)

            self.start_x = None
            self.start_y = None
            self._clear_rectangle()

            if self.crop_complete:
                self.crop_complete(img_x1, img_y1, img_x2, img_y2)

class ImageEditorApp:

    def __init__(self, root):
        self.root = root
        self.root.title("S125 HIT137 SOFTWARE NOW, Assignment-3")
        self.root.geometry("1200x800")

        self.image_processor = ImageCropApp()

        self._create_widgets()


    def _create_widgets(self):

        control_frame = tk.Frame(self.root, bd=2, padx=10, pady=10)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        self.load_button = tk.Button(control_frame, text="Load Image", command=self.load_image)
        self.load_button.pack(side=tk.LEFT, padx=5)

        self.crop_button = tk.Button(control_frame, text="Enable Cropping", command=self.toggle_cropping,
                                     state=tk.DISABLED)
        self.crop_button.pack(side=tk.LEFT, padx=5)

        self.save_button = tk.Button(control_frame, text="Save Modified Image", command=self.save_modified_image,
                                     state=tk.DISABLED)
        self.save_button.pack(side=tk.LEFT, padx=5)


        image_display_frame = tk.Frame(self.root, bd=2)
        image_display_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.original_image_viewer = ImageViewer(image_display_frame, 550, 450, self.image_processor)
        self.original_image_viewer.canvas.config(bg="#F0F0F0")
        self.original_image_viewer.set_crop_disable()

        self.modified_image_viewer = ImageViewer(image_display_frame, 550, 450, self.image_processor)
        self.modified_image_viewer.set_crop_complete(self._on_crop_region_selected)
        self.modified_image_viewer.set_crop_disable()

        resize_frame = tk.Frame(self.root, bd=2, padx=10, pady=10)
        resize_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        tk.Label(resize_frame, text="Resize Factor:").pack(side=tk.LEFT, padx=5)
        self.resize_slider = ttk.Scale(resize_frame, from_=0.1, to=2.0, orient=tk.HORIZONTAL,
                                       command=self.update_resized_image)
        self.resize_slider.set(0.0)
        self.resize_slider.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        self.resize_value_label = tk.Label(resize_frame, text="1.00x")
        self.resize_value_label.pack(side=tk.LEFT, padx=5)

    def load_image(self):

        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff"), ("All files", "*.*")]
        )
        if file_path:
            if self.image_processor.load_image(file_path):
                self.original_image_viewer.display_image(self.image_processor.original_image_cv)

                self.modified_image_viewer.display_image(self.image_processor.original_image_cv)
                self.image_processor.current_image_cv = self.image_processor.original_image_cv.copy()
                self.image_processor.cropped_image_cv = self.image_processor.original_image_cv.copy()

                self.crop_button.config(state=tk.NORMAL)
                self.save_button.config(state=tk.NORMAL)
                self.resize_slider.config(state=tk.NORMAL)
                self.resize_slider.set(1.0)  # Reset slider
                self.resize_value_label.config(text="1.00x")
                self.toggle_cropping(force_disable=True)
            else:
                self.crop_button.config(state=tk.DISABLED)
                self.save_button.config(state=tk.DISABLED)
                self.resize_slider.config(state=tk.DISABLED)

    def toggle_cropping(self, force_disable=False):
        """Toggles cropping mode for the modified image viewer."""
        if force_disable or self.modified_image_viewer.crop_enable:
            self.modified_image_viewer.set_crop_disable()
            self.crop_button.config(text="Enable Cropping")
        else:
            self.modified_image_viewer.set_crop_enable()
            self.crop_button.config(text="Disable Cropping (Click & Drag)")

    def _on_crop_region_selected(self, x1, y1, x2, y2):

        self.toggle_cropping(force_disable=True)

        cropped_img_cv = self.image_processor.crop(x1, y1, x2, y2)
        if cropped_img_cv is not None:
            self.modified_image_viewer.display_image(cropped_img_cv)

            self.resize_slider.set(1.0)
            self.resize_value_label.config(text="1.00x")
        else:
            messagebox.showwarning("Warning", "Invalid crop selection. Please drag a valid rectangle.")

    def update_resized_image(self, value):
        scale_factor = float(value)
        self.resize_value_label.config(text=f"{scale_factor:.2f}x")

        if self.image_processor.cropped_image_cv is not None:
            resized_img_cv = self.image_processor.resize(scale_factor)
            self.modified_image_viewer.display_image(resized_img_cv)
        else:
            if self.image_processor.current_image_cv is not None:
                temp_cropped = self.image_processor.current_image_cv
                self.image_processor.cropped_image_cv = temp_cropped
                resized_img_cv = self.image_processor.resize(scale_factor)
                self.modified_image_viewer.display_image(resized_img_cv)
                self.image_processor.cropped_image_cv = None # Reset it
            else:
                messagebox.showwarning("Warning", "Please load an image first to resize.")


    def save_modified_image(self):
        current_display_image = self.modified_image_viewer.display_image_cv

        if current_display_image is None:
            messagebox.showwarning("Warning", "No image to save. Please load and modify an image first.")
            return

        save_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
        )
        if save_path:
            self.image_processor.save_img(current_display_image, save_path)




if __name__ == "__main__":
    root = tk.Tk()
    app = ImageEditorApp(root)
    root.mainloop()


