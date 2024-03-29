import customtkinter
# import json
import os
import vars
import requests
import sys

sys.path.insert(1, './src/')
from common import *
import adbdevice
import battery
import brightness
import install
import plevel
import refresh
import texture
import ffr
import capture
import fps
import bitrate

customtkinter.set_appearance_mode("system")  # Modes: system (default), light, dark
customtkinter.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

def set_theme(choice):
    customtkinter.set_appearance_mode(choice)

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.geometry("400x400")
        self.title("Oculus manager")
        self.minsize(width=360, height=400)

        # ---------------------------------------------------------------------------- #
        #                                Create tabview                                #
        # ---------------------------------------------------------------------------- #
        self.tabview = customtkinter.CTkTabview(self, width=500)
        self.tabview.pack(padx=10, pady=10, fill="both", expand=True)

        self.general_tab = self.tabview.add("General")
        self.performance_tab = self.tabview.add("Performance")
        self.recording_tab = self.tabview.add("Recording")
        self.misc_tab = self.tabview.add("Misc")
        self.settings_tab = self.tabview.add("Settings")

        self.my_battery = battery.Battery
        self.my_brightness = brightness.Brightness
        self.my_p_level = plevel.PLevel

        self.general()
        self.performance()
        self.recording()
        self.misc()
        self.settings()


    # ---------------------------------------------------------------------------- #
    #                                    General                                   #
    # ---------------------------------------------------------------------------- #
    def general(self):
        # Brightness
        self.brightness_lbl = customtkinter.CTkLabel(self.general_tab, text="Brightness:")
        brightness_slider = customtkinter.CTkSlider(self.general_tab, from_=0, to=255, command=self.my_brightness.set)
        brightness_slider.set(int(self.my_brightness.get()))
        self.brightness_lbl.pack(side="top", anchor="w")
        brightness_slider.pack(side="top", anchor="w", padx=20)

        # Battery bars
        self.l_bat_pro = customtkinter.CTkProgressBar(self.general_tab)
        self.r_bat_pro = customtkinter.CTkProgressBar(self.general_tab)
        self.hmd_bat_pro = customtkinter.CTkProgressBar(self.general_tab)

        self.l_bat_pro.set(int(self.my_battery.get_l()) / 100)
        self.r_bat_pro.set(int(self.my_battery.get_r()) / 100)
        self.hmd_bat_pro.set(int(self.my_battery.get_hmd()) / 100)

        # Battery labels
        self.hmd_bat_lbl = customtkinter.CTkLabel(self.general_tab) # text gets updated in refresh()
        self.l_bat_lbl = customtkinter.CTkLabel(self.general_tab) # text gets updated in refresh()
        self.r_bat_lbl = customtkinter.CTkLabel(self.general_tab) # text gets updated in refresh()

        # Place battery labels and bars
        self.hmd_bat_lbl.pack(side="top", anchor="w", pady=(10, 0))
        self.hmd_bat_pro.pack(side="top", anchor="w", padx=20)

        self.l_bat_lbl.pack(side="top", anchor="w", pady=(10, 0))
        self.l_bat_pro.pack(side="top", anchor="w", padx=20)

        self.r_bat_lbl.pack(side="top", anchor="w", pady=(10, 0))
        self.r_bat_pro.pack(side="top", anchor="w", padx=20)

        # Refresh rate
        refresh_lbl = customtkinter.CTkLabel(self.general_tab, text="Refresh rate:")
        refresh_button = customtkinter.CTkSegmentedButton(self.general_tab, values=["60Hz", "72Hz", "90Hz", "120Hz"], command=refresh.RefreshRate.set)
        refresh_button.set(refresh.RefreshRate.get())

        refresh_lbl.pack(side="top", anchor="w", pady=(10, 0))
        refresh_button.pack(side="top", anchor="w", padx=10)

        # Proximity sensor
        prox_lbl = customtkinter.CTkLabel(self.general_tab, text="Proximity sensor:")
        self.prox_var = customtkinter.StringVar(value="on")
        prox_switch = customtkinter.CTkSwitch(self.general_tab, text="Proximity sensor", command=self.prox, variable=self.prox_var, onvalue="on", offvalue="off")
        prox_lbl.pack(side="top", anchor="w", pady=(10, 0))
        prox_switch.pack(side="top", anchor="w", padx=20)

    # ---------------------------------------------------------------------------- #
    #                                  Performance                                 #
    # ---------------------------------------------------------------------------- #
    def performance(self):
        cpu_lbl = customtkinter.CTkLabel(self.performance_tab, text="cpu level")
        gpu_lbl = customtkinter.CTkLabel(self.performance_tab, text="gpu level")

        cpu_button = customtkinter.CTkSegmentedButton(self.performance_tab, values=["0", "1", "2", "3", "4"], command=self.my_p_level.cpu)
        gpu_button = customtkinter.CTkSegmentedButton(self.performance_tab, values=["0", "1", "2", "3", "4"], command=self.my_p_level.gpu)
        cpu_lbl.pack(side="top", anchor="w")
        cpu_button.pack(side="top", anchor="w", padx=10)
        gpu_lbl.pack(side="top", anchor="w", pady=(10, 0))
        gpu_button.pack(side="top", anchor="w", padx=10)

        # texture values from sidequest
        tex_size_lbl = customtkinter.CTkLabel(self.performance_tab, text="Texture size:")
        tex_size_cb = customtkinter.CTkComboBox(self.performance_tab, values=["default", "512", "768", "1024", "1280", "1440", "1536", "2048", "2560", "3072"], command=texture.set_texture)
        tex_size_lbl.pack(side="top", anchor="w", pady=(10, 0))
        tex_size_cb.pack(side="top", anchor="w", padx=10)

        # ffr
        my_ffr = ffr.FFR

        ffr_lbl = customtkinter.CTkLabel(self.performance_tab, text="FFR:")
        ffr_cb = customtkinter.CTkComboBox(self.performance_tab, values=["off", "low", "medium", "high", "max"], command=my_ffr.set)
        ffr_lbl.pack(side="top", anchor="w", pady=(10, 0))
        ffr_cb.pack(side="top", anchor="w", padx=10)

        # dynamic ffr
        self.dffr_var = customtkinter.StringVar(value="on")
        dffr_lbl = customtkinter.CTkLabel(self.performance_tab, text="Dynamic FFR:")
        dffr_switch = customtkinter.CTkSwitch(self.performance_tab, text="Enable dynamic FFR", command=self.toggle_dffr, variable=self.dffr_var, onvalue="on", offvalue="off")
        dffr_lbl.pack(side="top", anchor="w", pady=(10, 0))
        dffr_switch.pack(side="top", anchor="w", padx=10)

    # ---------------------------------------------------------------------------- #
    #                                   Recording                                  #
    # ---------------------------------------------------------------------------- #
    def recording(self):
        # capture size
        cs_lbl = customtkinter.CTkLabel(self.recording_tab, text="Capture size")
        cs_cb = customtkinter.CTkComboBox(self.recording_tab, values=["640x480", "1280x720", "1920x1080", "1024x1024 (default)", "1600x1600"], width=170, command=capture.set_cs)
        cs_cb.set("1024x1024 (default)")
        cs_lbl.pack(side="top", anchor="w")
        cs_cb.pack(side="top", anchor="w", padx=10)

        # fps
        fps_lbl = customtkinter.CTkLabel(self.recording_tab, text="FPS:")
        fps_cb = customtkinter.CTkComboBox(self.recording_tab, values=["24fps", "30fps", "60fps"], command=fps.set_fps)
        fps_lbl.pack(side="top", anchor="w", pady=(10, 0))
        fps_cb.pack(side="top", anchor="w", padx=10)


        # Bitrate
        bitrate_lbl = customtkinter.CTkLabel(self.recording_tab, text="Bitrate:")
        bitrate_cb = customtkinter.CTkComboBox(self.recording_tab, values=["5mbps", "10mbps", "15mbps", "20mbps"], command=bitrate.set_bitrate)
        bitrate_lbl.pack(side="top", anchor="w", pady=(10, 0))
        bitrate_cb.pack(side="top", anchor="w", padx=10)

    # ---------------------------------------------------------------------------- #
    #                                     Misc                                     #
    # ---------------------------------------------------------------------------- #
    def misc(self):
        apk_install_lbl = customtkinter.CTkLabel(self.misc_tab, text="Install apk:")
        apk_install_btn = customtkinter.CTkButton(self.misc_tab, text="Choose apk to install", command=install.install_apk)
        apk_install_lbl.pack(side="top", anchor="w")
        apk_install_btn.pack(side="top", anchor="w", padx=10)

        self.kill_var = customtkinter.StringVar(value="off")
        if self.get_killer():
            self.kill_var.set(value="on")
        else:
            self.kill_var.set(value="off")
        killer_lbl = customtkinter.CTkLabel(self.misc_tab, text="Oculus killer v2:")
        killer_switch = customtkinter.CTkSwitch(self.misc_tab, text="Enable Oculus Killer v2 (unstable)", command=self.install_killer_v2, variable=self.kill_var, onvalue="on", offvalue="off")
        killer_lbl.pack(side="top", anchor="w", pady=(10, 0))
        killer_switch.pack(side="top", anchor="w", padx=10)

        self.guard_var = customtkinter.StringVar(value="on")
        guard_lbl = customtkinter.CTkLabel(self.misc_tab, text="Guardian:")
        guard_switch = customtkinter.CTkSwitch(self.misc_tab, text="Enable guardian", command=self.toggle_guard, variable=self.guard_var, onvalue="on", offvalue="off")
        guard_lbl.pack(side="top", anchor="w", pady=(10, 0))
        guard_switch.pack(side="top", anchor="w", padx=10)

        self.chroma_var = customtkinter.StringVar(value="on")
        chroma_lbl = customtkinter.CTkLabel(self.misc_tab, text="Chromatic aberration:")
        chroma_switch = customtkinter.CTkSwitch(self.misc_tab, text="Enable Chromatic aberration", command=self.toggle_chroma, variable=self.chroma_var, onvalue="on", offvalue="off")
        chroma_lbl.pack(side="top", anchor="w", pady=(10, 0))
        chroma_switch.pack(side="top", anchor="w", padx=10)

        self.experimental_var = customtkinter.StringVar(value="on")
        experimental_lbl = customtkinter.CTkLabel(self.misc_tab, text="experimental features:")
        experimental_switch = customtkinter.CTkSwitch(self.misc_tab, text="Enable experimental features", command=self.toggle_experimental, variable=self.experimental_var, onvalue="on", offvalue="off")
        experimental_lbl.pack(side="top", anchor="w", pady=(10, 0))
        experimental_switch.pack(side="top", anchor="w", padx=10)

    # ---------------------------------------------------------------------------- #
    #                                   Settings                                   #
    # ---------------------------------------------------------------------------- #
    def settings(self):
        theme = customtkinter.CTkComboBox(self.settings_tab, values=["system", "light", "dark"], command=set_theme)
        theme.pack()

        my_font = customtkinter.CTkFont(size=18)
        love_lbl = customtkinter.CTkLabel(self.settings_tab, text="Made with 💖", font=my_font)
        love_lbl.pack(side="bottom", anchor="s")

    # ---------------------------------------------------------------------------- #
    #                                    Refresh                                   #
    # ---------------------------------------------------------------------------- #
    def refresh(self):
        self.brightness_lbl.configure(text="Brightness: " + str(round((int(self.my_brightness.get()) / 255 * 100))) + "%")

        l_bat = self.my_battery.get_l()
        r_bat = self.my_battery.get_r()
        hmd_bat = self.my_battery.get_hmd()

        self.l_bat_pro.set(int(l_bat) / 100)
        self.r_bat_pro.set(int(r_bat) / 100)
        self.hmd_bat_pro.set(int(hmd_bat) / 100)
        self.l_bat_lbl.configure(text="Left controller battery: " + l_bat + "%")
        self.r_bat_lbl.configure(text="Right controller battery: " + r_bat + "%")
        self.hmd_bat_lbl.configure(text="Headset battery: " + hmd_bat + "%")

        if int(hmd_bat) <= 20 and int(hmd_bat) > 15:
            self.hmd_bat_pro.configure(progress_color="#B3B526")
        elif int(hmd_bat) <= 15:
            self.hmd_bat_pro.configure(progress_color="#750E00")
        else:
            self.hmd_bat_pro.configure(progress_color="#1F6AA5")

        if int(l_bat) <= 20 and int(l_bat) > 15:
            self.l_bat_pro.configure(progress_color="#B3B526")
        elif int(l_bat) <= 15:
            self.l_bat_pro.configure(progress_color="#750E00")
        else:
            self.l_bat_pro.configure(progress_color="#1F6AA5")

        if int(r_bat) <= 20 and int(r_bat) > 15:
            self.r_bat_pro.configure(progress_color="#B3B526")
        elif int(r_bat) <= 15:
            self.r_bat_pro.configure(progress_color="#750E00")
        else:
            self.r_bat_pro.configure(progress_color="#1F6AA5")

        self.after(5000, self.refresh)

    def prox(self):
        logger.debug("Prox:" + self.prox_var.get())
        if not vars.debug:
            if self.prox_var.get() == "on":
                adbdevice.device.shell("am broadcast -a com.oculus.vrpowermanager.automation_disable")
            else:
                adbdevice.device.shell("am broadcast -a com.oculus.vrpowermanager.prox_close")

    def install_killer_v2(self):
        current_user = os.getlogin()
        if self.kill_var.get() == "on":
            if not os.path.exists('C:/Program Files/Oculus/Support/oculus-dash/dash/bin/version.dll'):
                logger.debug(os.path.exists(f"C:/Users/{current_user}/Downloads/version.dll"))
                if not os.path.exists(f"C:/Users/{current_user}/Downloads/version.dll"):
                    url = 'https://cdn.discordapp.com/attachments/1062101939246088233/1062104363465711716/version.dll' # TODO: change this when stable version is out
                    file = requests.get(url)
                    open(f'C:/Users/{current_user}/Downloads/version.dll', 'wb').write(file.content)
                os.system("Powershell Start ./killer.bat -Verb Runas")
        elif self.kill_var.get() == "off":
            if os.path.exists('C:/Program Files/Oculus/Support/oculus-dash/dash/bin/version.dll'):
                os.remove('C:/Program Files/Oculus/Support/oculus-dash/dash/bin/version.dll')

    def get_killer(self):
        return os.path.exists("C:\\Program Files\\Oculus\\Support\\oculus-dash\\dash\\bin\\version.dll")

    def toggle_guard(self):
        logger.debug("Gaurdian: " + self.guard_var.get())
        if self.guard_var.get() == "on":
            adbdevice.device.shell("setprop debug.oculus.guardian_pause 1")
        elif self.guard_var.get() == "off":
            adbdevice.device.shell("setprop debug.oculus.guardian_pause 0")

    def toggle_chroma(self):
        logger.debug("Chroma: " + self.chroma_var.get())
        if self.chroma_var.get() == "on":
            adbdevice.device.shell("setprop debug.oculus.forceChroma 1")
        elif self.chroma_var.get() == "off":
            adbdevice.device.shell("setprop debug.oculus.forceChroma 0")

    def toggle_experimental(self):
        logger.debug("Experimental: " + self.experimental_var.get())
        if self.experimental_var.get() == "on":
            adbdevice.device.shell("setprop debug.oculus.experimentalEnabled 1")
        elif self.experimental_var.get() == "off":
            adbdevice.device.shell("setprop debug.oculus.experimentalEnabled 0")

    def toggle_dffr(self):
        logger.debug("DFFR: " + self.dffr_var.get())
        if self.dffr_var.get() == "on":
            adbdevice.device.shell("setprop debug.oculus.foveation.dynamic 1")
        elif self.dffr_var.get() == "off":
            adbdevice.device.shell("setprop debug.oculus.foveation.dynamic 0")

# ---------------------------------------------------------------------------- #
#                                     Loop                                     #
# ---------------------------------------------------------------------------- #
if __name__ == "__main__":
    if adbdevice.adb_connected or vars.debug:
        if vars.debug:
            logger.info("running in debug mode")
        app = App()
        app.refresh()
        app.mainloop()