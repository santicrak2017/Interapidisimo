

import customtkinter as ctk
from ui.screens import LoginScreen, HomeScreen, TablesScreen, LocalidadesScreen


class App(ctk.CTk):
  

    def __init__(self):
        super().__init__()

        # ── Configuración de la ventana ───────────────
        self.title("Inter Rapidísimo — Sistema de Gestión")
        self.geometry("720x580")
        self.minsize(640, 520)
        self.configure(fg_color="#0D0D0D")

        try:
            self.iconbitmap("assets/icon.ico")
        except Exception:
            pass

   
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

     
        self.frames: dict[str, ctk.CTkFrame] = {}
        self._register_screens()

        # ── Pantalla inicial ──────────────────────────
        self.show_frame("LoginScreen")

    def _register_screens(self):
        
        screens = {
            "LoginScreen":      LoginScreen,
            "HomeScreen":       HomeScreen,
            "TablesScreen":     TablesScreen,
            "LocalidadesScreen": LocalidadesScreen,
        }
        for name, ScreenClass in screens.items():
            frame = ScreenClass(parent=self, controller=self)
            self.frames[name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

    def show_frame(self, name: str, **kwargs):
      
        frame = self.frames.get(name)
        if not frame:
            raise ValueError(f"Pantalla '{name}' no registrada.")

        # Pasar datos si la pantalla lo soporta
        if kwargs.get("user") and hasattr(frame, "load_user"):
            frame.load_user(kwargs["user"])

        frame.tkraise()




if __name__ == "__main__":
    try:
        app = App()
        app.mainloop()
    except KeyboardInterrupt:
        print("\nAplicación cerrada por el usuario.")
    except Exception as e:
        print(f"Error fatal al iniciar la aplicación: {e}")
        raise
