import tkinter as tk

button_pressed = False

def popup_window_with_timeout(text):
    global button_pressed 

    def button_click():
        global button_pressed
        button_pressed = True
        root.destroy()

    def close_window():
        root.destroy()

    button_pressed = False 

    root = tk.Tk()
    root.title("DUE IN TEN MINUTES")
    root.geometry("500x100")

    label = tk.Label(root, text=text, font=("Arial", 12))
    label.pack(pady=20)

    button = tk.Button(root, text="Got it", command=button_click, font=("Arial", 10))
    button.pack(pady=10)

    root.after(10000, close_window)
    root.mainloop()

    return button_pressed

