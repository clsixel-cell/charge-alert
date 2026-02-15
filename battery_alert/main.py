from kivy.app import App
from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from datetime import datetime
from plyer import battery, notification

# ===============================
# 🔧 Developer Config
# ===============================
APP_ICON = "icon2.png"
ALERT_SOUND = "Alert.mp3"
# ===============================

KV = """
BoxLayout:
    orientation: "vertical"
    padding: 20
    spacing: 10
    canvas.before:
        Color:
            rgba: 0.93, 0.89, 0.74, 1
        Rectangle:
            pos: self.pos
            size: self.size

    Label:
        text: "I forget to charge my phone application"
        font_size: 22
        bold: True
        size_hint_y: None
        height: 60
        color: 0,0,0,1

    BoxLayout:
        orientation: "vertical"
        padding: 20
        spacing: 15
        canvas.before:
            Color:
                rgba: 1,1,1,1
            RoundedRectangle:
                pos: self.pos
                size: self.size
                radius: [25]

        Label:
            text: "Notify me when battery lower than:"
            color: 0,0,0,1

        TextInput:
            id: battery_input
            hint_text: "Battery %"
            input_filter: "int"
            multiline: False
            size_hint_y: None
            height: 40
            background_color: 1, 0.88, 0.65, 1

        Label:
            text: "Notify me at time:"
            color: 0,0,0,1

        BoxLayout:
            size_hint_y: None
            height: 40
            spacing: 5

            TextInput:
                id: hour_input
                hint_text: "HH"
                input_filter: "int"
                multiline: False
                background_color: 1, 0.88, 0.65, 1

            Label:
                text: ":"
                size_hint_x: None
                width: 15
                color: 0,0,0,1

            TextInput:
                id: minute_input
                hint_text: "mm"
                input_filter: "int"
                multiline: False
                background_color: 1, 0.88, 0.65, 1

        BoxLayout:
            size_hint_y: None
            height: 40
            spacing: 10

            Label:
                text: "Repeat every day"
                color: 0,0,0,1

            Switch:
                id: daily_switch
                active: False

        Button:
            text: "Confirm"
            size_hint_y: None
            height: 45
            background_normal: ""
            background_color: 0.62, 0.75, 0.65, 1
            color: 0,0,0,1
            on_press: app.start_reminder()

    Button:
        text: "How to use"
        size_hint_y: None
        height: 45
        background_normal: ""
        background_color: 1, 0.88, 0.65, 1
        color: 0,0,0,1
        on_press: app.show_how_to_use()

    Label:
        text: "note: set the time 5 minutes before bed"
        font_size: 20
        color: 0,0,0,1
"""

class ChargeReminderApp(App):

    def build(self):
        self.last_trigger_date = None
        self.alert_sound = None
        self.icon = APP_ICON  # ตั้งค่า icon ทันที
        return Builder.load_string(KV)

    def start_reminder(self):
        try:
            self.target_battery = int(self.root.ids.battery_input.text)
            self.target_hour = int(self.root.ids.hour_input.text)
            self.target_minute = int(self.root.ids.minute_input.text)

            if not (0 <= self.target_hour <= 23 and
                    0 <= self.target_minute <= 59 and
                    1 <= self.target_battery <= 100):
                raise ValueError

            self.daily_mode = self.root.ids.daily_switch.active

            Clock.unschedule(self.check_condition)
            Clock.schedule_interval(self.check_condition, 1)  # เช็คทุก 1 วิ

            self.show_popup("Success", "System is running successfully.")

        except:
            self.show_popup("Error", "Please enter valid time and battery percentage.")

    def check_condition(self, dt):
        now = datetime.now()
        today = now.date()

        batt = battery.status
        if not batt or batt["percentage"] is None:
            return

        current_battery = batt["percentage"]

        if (now.hour == self.target_hour and
            now.minute == self.target_minute and
            current_battery <= self.target_battery):

            if self.daily_mode:
                if self.last_trigger_date == today:
                    return
                self.last_trigger_date = today
            else:
                Clock.unschedule(self.check_condition)

            self.send_push_notification(current_battery)
            self.play_alert_sound()

    def send_push_notification(self, battery_percent):
        notification.notify(
            title="Battery Alert",
            message=f"Battery is {battery_percent}%\nTime to charge your phone!",
            timeout=10
        )

    def play_alert_sound(self):
        # โหลดเสียงเฉพาะตอนใช้งานจริง → ไม่ดีเลย์ตอนเปิดแอป
        sound = SoundLoader.load(ALERT_SOUND)
        if sound:
            sound.play()

    def show_how_to_use(self):
        self.show_popup(
            "How to use",
            "1. Enter battery percentage\n"
            "2. Enter time\n"
            "3. Enable daily mode if needed\n"
            "4. Press Confirm"
        )

    def show_popup(self, title, message):
        Popup(
            title=title,
            content=Label(text=message),
            size_hint=(0.8, 0.6),
            auto_dismiss=True
        ).open()


if __name__ == "__main__":
    ChargeReminderApp().run()
