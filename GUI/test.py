from tkinter import *
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw, ImageOps


class ProfilePictureApp:
    def __init__(self, parent):
        self.parent = parent

        # Canvas for profile picture
        self.canvas_width = 300
        self.canvas_height = 300
        self.canvas = Canvas(self.parent, width=self.canvas_width, height=self.canvas_height, bg='grey')
        self.canvas.pack()

        # Placeholder for selected image
        self.selected_image = None
        self.tk_img = None
        self.image_on_canvas = None
        self.img_x = 0
        self.img_y = 0
        self.scale_factor = 1.0

        # Draw initial circle
        self.circle_radius = 150
        self.circle_center = [self.canvas_width // 2, self.canvas_height // 2]
        self.circle = self.canvas.create_oval(self.circle_center[0] - self.circle_radius,
                                              self.circle_center[1] - self.circle_radius,
                                              self.circle_center[0] + self.circle_radius,
                                              self.circle_center[1] + self.circle_radius,
                                              outline='white', width=2)

        # Upload button
        self.upload_btn = Button(self.parent, text="Upload Profile Picture", command=self.upload_picture)
        self.upload_btn.pack(pady=10)

        # Crop button
        self.crop_btn = Button(self.parent, text="Crop", command=self.crop_picture, state=DISABLED)
        self.crop_btn.pack(pady=10)

        # Zoom buttons
        self.zoom_in_btn = Button(self.parent, text="Zoom In", command=self.zoom_in)
        self.zoom_in_btn.pack(side=LEFT, padx=10)
        self.zoom_out_btn = Button(self.parent, text="Zoom Out", command=self.zoom_out)
        self.zoom_out_btn.pack(side=LEFT)

        # Mouse bindings for moving the image
        self.canvas.bind("<ButtonPress-1>", self.start_move)
        self.canvas.bind("<B1-Motion>", self.move_image)

    def upload_picture(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if file_path:
            self.selected_image = Image.open(file_path)
            if min(self.selected_image.width, self.selected_image.height) < 2 * self.circle_radius:
                messagebox.showerror("Error", "Image too small. Please select a larger image.")
                return
            self.show_preview(self.selected_image)
            self.canvas.tag_raise(self.circle)  # Raise the circle to ensure it's always on top
            self.crop_btn.configure(state=NORMAL)

    def show_preview(self, img):
        # Resize image to fit canvas size while maintaining aspect ratio
        img.thumbnail((self.canvas_width, self.canvas_height))
        img = img.resize((int(img.width * self.scale_factor), int(img.height * self.scale_factor)))
        self.tk_img = ImageTk.PhotoImage(img)
        if self.image_on_canvas is None:
            self.image_on_canvas = self.canvas.create_image(self.canvas_width // 2, self.canvas_height // 2,
                                                            anchor='center', image=self.tk_img)
        else:
            self.canvas.itemconfig(self.image_on_canvas, image=self.tk_img)

    def crop_picture(self):
        # Calculate cropping area based on the circle position and radius
        x = self.circle_center[0] - self.circle_radius
        y = self.circle_center[1] - self.circle_radius
        diameter = 2 * self.circle_radius

        # Convert coordinates to match scaled canvas size
        x_scaled = int(x / self.scale_factor)
        y_scaled = int(y / self.scale_factor)
        diameter_scaled = int(diameter / self.scale_factor)

        # Create mask for the circle
        mask = Image.new("L", (self.canvas_width, self.canvas_height), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((x_scaled, y_scaled, x_scaled + diameter_scaled, y_scaled + diameter_scaled), fill=255)

        # Apply mask to the image
        cropped = ImageOps.fit(self.selected_image, mask.size, centering=(0.5, 0.5))
        cropped.putalpha(mask)

        # Crop the image to retain only the part inside the circle
        cropped = cropped.crop((x_scaled, y_scaled, x_scaled + diameter_scaled, y_scaled + diameter_scaled))

        # Display cropped image
        self.show_preview(cropped)

    def start_move(self, event):
        self.img_x = event.x
        self.img_y = event.y

    def move_image(self, event):
        delta_x = event.x - self.img_x
        delta_y = event.y - self.img_y
        self.canvas.move(self.image_on_canvas, delta_x, delta_y)
        self.circle_center[0] += delta_x
        self.circle_center[1] += delta_y
        self.img_x = event.x
        self.img_y = event.y

    def zoom_in(self):
        self.scale_factor *= 1.1
        if self.selected_image:
            self.show_preview(self.selected_image)

    def zoom_out(self):
        self.scale_factor /= 1.1
        if self.selected_image:
            self.show_preview(self.selected_image)


if __name__ == "__main__":
    root = Tk()
    app = ProfilePictureApp(root)
    root.mainloop()
