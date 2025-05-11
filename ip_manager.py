import customtkinter as ctk
import subprocess
import platform
import psutil
import socket
from PIL import Image, ImageTk
import io
import base64

# Configuración de la interfaz
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class IPManager(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("IP Manager Avanzado")
        self.geometry("600x500")
        
        # Variables para la IP
        self.ip_parts = ["192", "168", "1", "182"]
        self.subnet_mask = "255.255.255.0"
        self.gateway = "192.168.1.1"
        self.dns1 = "8.8.4.4"
        self.dns2 = "8.8.8.8"
        
        self.wifi_img = ctk.CTkImage(light_image=Image.open("assets/wifi.png"), dark_image=Image.open("assets/wifi.png"), size=(64, 64))
        self.ethernet_img = ctk.CTkImage(light_image=Image.open("assets/ethernet.png"), dark_image=Image.open("assets/ethernet.png"), size=(64, 64))
        
        self.create_widgets()
        self.update_network_info()
    
    def load_base64_image(self, base64_str):
        image_data = base64.b64decode(base64_str)
        image = Image.open(io.BytesIO(image_data))
        return ctk.CTkImage(light_image=image, dark_image=image, size=(64, 64))
    
    def create_widgets(self):
        # Frame principal
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Título
        self.title_label = ctk.CTkLabel(self.main_frame, text="IP MANAGER AVANZADO",font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.pack(pady=(10, 20))
        
        # Frame de información de red
        self.info_frame = ctk.CTkFrame(self.main_frame)
        self.info_frame.pack(pady=10, padx=10, fill="x")
        
        # Icono y tipo de conexión
        self.connection_icon = ctk.CTkLabel(self.info_frame, image=self.wifi_img, text="")
        self.connection_icon.grid(row=0, column=0, rowspan=3, padx=10, pady=10)
        
        self.connection_type_label = ctk.CTkLabel(self.info_frame, text="Tipo de conexión: ",font=ctk.CTkFont(weight="bold"))
        self.connection_type_label.grid(row=0, column=1, sticky="w")
        
        self.connection_type = ctk.CTkLabel(self.info_frame, text="Desconocido")
        self.connection_type.grid(row=0, column=2, sticky="w")
        
        # IP actual
        self.current_ip_label = ctk.CTkLabel(self.info_frame, text="IP actual: ",font=ctk.CTkFont(weight="bold"))
        self.current_ip_label.grid(row=1, column=1, sticky="w")
        
        self.current_ip = ctk.CTkLabel(self.info_frame, text="0.0.0.0")
        self.current_ip.grid(row=1, column=2, sticky="w")
        
        # Latencia
        self.latency_label = ctk.CTkLabel(self.info_frame, text="Latencia: ",font=ctk.CTkFont(weight="bold"))
        self.latency_label.grid(row=2, column=1, sticky="w")
        
        self.latency = ctk.CTkLabel(self.info_frame, text="0 ms")
        self.latency.grid(row=2, column=2, sticky="w")
        
        # Frame para configuración de IP
        self.ip_config_frame = ctk.CTkFrame(self.main_frame)
        self.ip_config_frame.pack(pady=10, padx=10, fill="x")
        
        ctk.CTkLabel(self.ip_config_frame, text="Configurar IP estática", 
                    font=ctk.CTkFont(weight="bold")).pack(pady=5)
        
        # Controles para editar la IP
        self.ip_controls_frame = ctk.CTkFrame(self.ip_config_frame)
        self.ip_controls_frame.pack(pady=10)
        
        for i in range(4):
            frame = ctk.CTkFrame(self.ip_controls_frame)
            frame.grid(row=0, column=i, padx=5)
            
            # Botón arriba
            up_btn = ctk.CTkButton(frame, text="↑", width=30, height=25,command=lambda idx=i: self.increment_ip_part(idx))
            up_btn.pack()
            
            # Parte de la IP
            entry = ctk.CTkEntry(frame, width=50, justify="center")
            entry.insert(0, self.ip_parts[i])
            entry.bind("<KeyRelease>", lambda e, idx=i: self.update_ip_part(e, idx))
            entry.pack(pady=5)
            
            # Botón abajo
            down_btn = ctk.CTkButton(frame, text="↓", width=30, height=25,command=lambda idx=i: self.decrement_ip_part(idx))
            down_btn.pack()
            
            # Punto después de cada parte excepto la última
            if i < 3:
                ctk.CTkLabel(self.ip_controls_frame, text=".").grid(row=0, column=i+1)
        
        # Botones de acción
        self.button_frame = ctk.CTkFrame(self.main_frame)
        self.button_frame.pack(pady=20)
        
        self.connect_btn = ctk.CTkButton(self.button_frame, text="CONECTARSE",command=self.set_static_ip, width=150, height=40)
        self.connect_btn.pack(side="left", padx=10)
        
        self.disconnect_btn = ctk.CTkButton(self.button_frame, text="DESCONECTARSE",command=self.set_dhcp, width=150, height=40)
        self.disconnect_btn.pack(side="left", padx=10)
        
        # Estado
        self.status_label = ctk.CTkLabel(self.main_frame, text="", text_color="white")
        self.status_label.pack(pady=10)
    
    def increment_ip_part(self, index):
        try:
            value = int(self.ip_parts[index])
            if value < 255:
                value += 1
                self.ip_parts[index] = str(value)
                self.update_ip_entries()
        except ValueError:
            pass
    
    def decrement_ip_part(self, index):
        try:
            value = int(self.ip_parts[index])
            if value > 0:
                value -= 1
                self.ip_parts[index] = str(value)
                self.update_ip_entries()
        except ValueError:
            pass
    
    def update_ip_part(self, event, index):
        widget = event.widget
        text = widget.get()
        if text.isdigit() and 0 <= int(text) <= 255:
            self.ip_parts[index] = text
    
    def update_ip_entries(self):
        for i, entry in enumerate(self.ip_controls_frame.winfo_children()):
            if isinstance(entry, ctk.CTkFrame):
                for child in entry.winfo_children():
                    if isinstance(child, ctk.CTkEntry):
                        child.delete(0, "end")
                        child.insert(0, self.ip_parts[i])
    
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
    
    def measure_latency(self):
        try:
            if platform.system() == "Windows":
                ping_process = subprocess.run(["ping", "-n", "1", "8.8.8.8"],capture_output=True, text=True, timeout=2)
            else:
                ping_process = subprocess.run(["ping", "-c", "1", "8.8.8.8"],capture_output=True, text=True, timeout=2)
            
            output = ping_process.stdout
            if "time=" in output:
                time_str = output.split("time=")[1].split(" ")[0]
                self.latency.config(text=f"{time_str} ms")
            else:
                self.latency.configure(text="No disponible")
        except Exception as e:
            self.latency.config(text="Error al medir")
            print(e)

    
    def update_network_info(self):
        interface = self.get_active_interface()
        connection_type = self.get_connection_type(interface)
        
        # Actualizar icono
        if "Wi-Fi" in connection_type:
            self.connection_icon.configure(image=self.wifi_img)
        else:
            self.connection_icon.configure(image=self.ethernet_img)
        
        self.connection_type.configure(text=connection_type)
        self.current_ip.configure(text=self.get_current_ip(interface))
        self.latency.configure(text=self.measure_latency())
        
        # Actualizar cada 5 segundos
        self.after(5000, self.update_network_info)
    
    def set_static_ip(self):
        interface = self.get_active_interface()
        if interface is None:
            self.status_label.configure(text="No se encontró interfaz activa", text_color="red")
            return
        
        static_ip = ".".join(self.ip_parts)
        
        if platform.system() == "Windows":
            try:
                # Configurar IP estática
                subprocess.run(["netsh", "interface", "ip", "set", "address",f"name={interface}", "static", static_ip,self.subnet_mask, self.gateway], check=True)
                
                # Configurar DNS
                subprocess.run(["netsh", "interface", "ip", "set", "dns",f"name={interface}", "static", self.dns1], check=True)
                subprocess.run(["netsh", "interface", "ip", "add", "dns",f"name={interface}", self.dns2, "index=2"], check=True)
                
                self.status_label.configure(text=f"IP estática configurada: {static_ip}",text_color="green")
                
                # Actualizar información después de 3 segundos
                self.after(3000, self.update_network_info)
            except subprocess.CalledProcessError as e:
                self.status_label.configure(text=f"Error al configurar IP: {e}",text_color="red")
        else:
            self.status_label.configure(text="Solo compatible con Windows",text_color="orange")
    
    def set_dhcp(self):
        interface = self.get_active_interface()
        if interface is None:
            self.status_label.configure(text="No se encontró interfaz activa", text_color="red")
            return
        
        if platform.system() == "Windows":
            try:
                # Volver a DHCP
                subprocess.run(["netsh", "interface", "ip", "set", "address",f"name={interface}", "dhcp"], check=True)
                subprocess.run(["netsh", "interface", "ip", "set", "dns",f"name={interface}", "dhcp"], check=True)
                
                self.status_label.configure(text="Modo DHCP activado", text_color="green")
                
                # Actualizar información después de 3 segundos
                self.after(3000, self.update_network_info)
            except subprocess.CalledProcessError as e:
                self.status_label.configure(text=f"Error al activar DHCP: {e}",text_color="red")
        else:
            self.status_label.configure(text="Solo compatible con Windows",text_color="orange")

if __name__ == "__main__":
    app = IPManager()
    app.mainloop()


#pip install pyinstaller
#

