import customtkinter as ctk
import subprocess
import platform
import psutil
import socket
import webbrowser

# Configuración de la interfaz
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class IPManager(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("IP Manager Avanzado")
        self.geometry("600x600")

        # Variables para la IP
        self.ip_vars = [ctk.StringVar(value=part) for part in ["192", "168", "1", "182"]]
        self.subnet_mask = "255.255.255.0"
        self.gateway = "192.168.1.1"
        self.dns1 = "8.8.4.4"
        self.dns2 = "8.8.8.8"

        self.create_widgets()
        self.update_network_info()

    def create_widgets(self):
        # Frame principal
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)

        # Título
        self.title_label = ctk.CTkLabel(self.main_frame, text="IP MANAGER AVANZADO", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.pack(pady=(10, 20))

        # Frame de información de red
        self.info_frame = ctk.CTkFrame(self.main_frame)
        self.info_frame.pack(pady=10, padx=10, fill="x")

        # Tipo de conexión
        self.connection_type_label = ctk.CTkLabel(self.info_frame, text="Tipo de conexión: ", font=ctk.CTkFont(weight="bold"))
        self.connection_type_label.grid(row=0, column=0, sticky="w")

        self.connection_type = ctk.CTkLabel(self.info_frame, text="Desconocido")
        self.connection_type.grid(row=0, column=1, sticky="w")

        # IP actual
        self.current_ip_label = ctk.CTkLabel(self.info_frame, text="IP actual: ", font=ctk.CTkFont(weight="bold"))
        self.current_ip_label.grid(row=1, column=0, sticky="w")

        self.current_ip = ctk.CTkLabel(self.info_frame, text="0.0.0.0")
        self.current_ip.grid(row=1, column=1, sticky="w")

        # Nombre de la red
        self.network_name_label = ctk.CTkLabel(self.info_frame, text="Red Wi-Fi: ", font=ctk.CTkFont(weight="bold"))
        self.network_name_label.grid(row=2, column=0, sticky="w")

        self.network_name = ctk.CTkLabel(self.info_frame, text="Desconocido")
        self.network_name.grid(row=2, column=1, sticky="w")

        # Frame para configuración de IP
        self.ip_config_frame = ctk.CTkFrame(self.main_frame)
        self.ip_config_frame.pack(pady=10, padx=10, fill="x")

        ctk.CTkLabel(self.ip_config_frame, text="Configurar IP estática", font=ctk.CTkFont(weight="bold")).pack(pady=5)

        # Controles para editar la IP
        self.ip_controls_frame = ctk.CTkFrame(self.ip_config_frame)
        self.ip_controls_frame.pack(pady=10)

        self.ip_entries = []
        for i in range(4):
            frame = ctk.CTkFrame(self.ip_controls_frame)
            frame.grid(row=0, column=i, padx=5)

            # Botón arriba
            up_btn = ctk.CTkButton(frame, text="↑", width=30, height=25, command=lambda idx=i: self.increment_ip_part(idx))
            up_btn.pack()

            # Parte de la IP
            entry = ctk.CTkEntry(frame, width=50, justify="center", textvariable=self.ip_vars[i])
            entry.pack(pady=5)
            self.ip_entries.append(entry)

            # Botón abajo
            down_btn = ctk.CTkButton(frame, text="↓", width=30, height=25, command=lambda idx=i: self.decrement_ip_part(idx))
            down_btn.pack()

            # Punto después de cada parte excepto la última
            if i < 3:
                ctk.CTkLabel(self.ip_controls_frame, text=".").grid(row=0, column=i+1)

        # Botones de acción
        self.button_frame = ctk.CTkFrame(self.main_frame)
        self.button_frame.pack(pady=20)

        self.connect_btn = ctk.CTkButton(self.button_frame, text="CONECTARSE", command=self.set_static_ip, width=150, height=40)
        self.connect_btn.pack(side="left", padx=10)

        self.disconnect_btn = ctk.CTkButton(self.button_frame, text="DESCONECTARSE", command=self.set_dhcp, width=150, height=40)
        self.disconnect_btn.pack(side="left", padx=10)

        # Estado
        self.status_label = ctk.CTkLabel(self.main_frame, text="", text_color="white")
        self.status_label.pack(pady=10)

        # Créditos
        self.credits_frame = ctk.CTkFrame(self.main_frame)
        self.credits_frame.pack(pady=10)

        self.credits_label = ctk.CTkLabel(self.credits_frame, text="Ing. Valerio Gomez", font=ctk.CTkFont(size=12, weight="bold"))
        self.credits_label.pack(padx=10, pady=5)
        self.credits_label.bind("<Button-1>", lambda e: self.open_credits_link())

    def open_credits_link(self):
        webbrowser.open("https://valerio-gomez.web.app/")

    def increment_ip_part(self, index):
        try:
            value = int(self.ip_vars[index].get())
            if value < 255:
                value += 1
                self.ip_vars[index].set(str(value))
        except ValueError:
            pass

    def decrement_ip_part(self, index):
        try:
            value = int(self.ip_vars[index].get())
            if value > 0:
                value -= 1
                self.ip_vars[index].set(str(value))
        except ValueError:
            pass




    def get_active_interface(self):
        interfaces = psutil.net_if_stats()
        for interface, stats in interfaces.items():
            if stats.isup:
                addrs = psutil.net_if_addrs().get(interface, [])
                for addr in addrs:
                    if addr.family == socket.AF_INET and not addr.address.startswith('127.'):
                        return interface
        return None

    def get_connection_type(self, interface):
        if interface is None:
            return "Desconocido"
        return "Wi-Fi" if "Wi-Fi" in interface or "Wireless" in interface else "Ethernet"

    def get_current_ip(self, interface):
        if interface is None:
            return "0.0.0.0"
        addrs = psutil.net_if_addrs().get(interface, [])
        for addr in addrs:
            if addr.family == socket.AF_INET:
                return addr.address
        return "0.0.0.0"

    def get_network_name(self):
        try:
            if platform.system() == "Windows":
                result = subprocess.run("netsh wlan show interfaces", capture_output=True, text=True, shell=True)
                for line in result.stdout.splitlines():
                    if "SSID" in line:
                        return line.split(":")[1].strip()
            elif platform.system() == "Linux":
                result = subprocess.run("iwgetid -r", capture_output=True, text=True, shell=True)
                return result.stdout.strip()
            else:
                return "Desconocido"
        except Exception:
            return "Desconocido"

    def update_network_info(self):
        interface = self.get_active_interface()
        connection_type = self.get_connection_type(interface)
        current_ip = self.get_current_ip(interface)
        network_name = self.get_network_name()

        self.connection_type.configure(text=connection_type)
        self.current_ip.configure(text=current_ip)
        self.network_name.configure(text=network_name)

    def set_static_ip(self):
        interface = self.get_active_interface()
        ip = self.ip_entry.get()
        subnet = self.subnet_entry.get()
        gateway = self.gateway_entry.get()
        dns = self.dns_entry.get()

        if not all([interface, ip, subnet, gateway, dns]):
            self.status_label.configure(text="Todos los campos deben estar completos", text_color="red")
            return

        if platform.system() == "Windows":
            try:
                # Establecer IP estática
                subprocess.run(
                    ["netsh", "interface", "ip", "set", "address", f"name={interface}", "static", ip, subnet, gateway, "1"],
                    check=True
                )
                # Establecer DNS
                subprocess.run(
                    ["netsh", "interface", "ip", "set", "dns", f"name={interface}", "static", dns],
                    check=True
                )
                self.status_label.configure(text="IP estática configurada correctamente", text_color="green")

                # Actualizar la información de red después de 3 segundos
                self.after(3000, self.update_network_info)
            except subprocess.CalledProcessError:
                self.status_label.configure(text="Error al configurar IP estática", text_color="red")

        else:
            self.status_label.configure(text="Sistema operativo no compatible", text_color="red")

    def set_dhcp(self):
        interface = self.get_active_interface()
        if interface is None:
            self.status_label.configure(text="No se encontró interfaz activa", text_color="red")
            return

        if platform.system() == "Windows":
            try:
                # Restablecer a DHCP
                subprocess.run(["netsh", "interface", "ip", "set", "address", f"name={interface}", "dhcp"], check=True)
                subprocess.run(["netsh", "interface", "ip", "set", "dns", f"name={interface}", "dhcp"], check=True)
                self.status_label.configure(text="Configurado a DHCP", text_color="green")

                # Actualizar información después de 3 segundos
                self.after(3000, self.update_network_info)
            except subprocess.CalledProcessError:
                self.status_label.configure(text="Error al configurar DHCP", text_color="red")
        else:
            self.status_label.configure(text="Sistema operativo no compatible", text_color="red")

if __name__ == "__main__":
    app = IPManager()
    app.mainloop()
