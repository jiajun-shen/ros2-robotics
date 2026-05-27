import math
import tkinter as tk

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node


class OnScreenJoystickNode(Node):
    """圆盘方向键：圆盘控制前后/横移，按钮控制原地转向。"""

    def __init__(self):
        super().__init__('quadruped_on_screen_joystick_node')

        self.declare_parameter('cmd_topic', 'cmd_vel')
        self.declare_parameter('max_linear_speed_mps', 0.65)
        self.declare_parameter('max_lateral_speed_mps', 0.42)
        self.declare_parameter('max_angular_speed_radps', 1.35)
        self.declare_parameter('publish_rate_hz', 20.0)

        self.cmd_topic = self.get_parameter('cmd_topic').value
        self.max_linear = float(self.get_parameter('max_linear_speed_mps').value)
        self.max_lateral = float(self.get_parameter('max_lateral_speed_mps').value)
        self.max_angular = float(self.get_parameter('max_angular_speed_radps').value)
        self.publish_rate = float(self.get_parameter('publish_rate_hz').value)

        self.linear_x = 0.0
        self.linear_y = 0.0
        self.angular_z = 0.0
        self.publisher = self.create_publisher(Twist, self.cmd_topic, 10)

        self.root = tk.Tk()
        self.root.title('ROS2 Wheel-Leg Dog Controller')
        self.root.geometry('460x650')
        self.root.configure(bg='#15191d')
        self.root.attributes('-topmost', True)
        self.root.protocol('WM_DELETE_WINDOW', self.close)

        self.pad_size = 340
        self.center = self.pad_size / 2
        self.outer_radius = 135
        self.knob_radius = 34
        self.dragging = False
        self.closed = False
        self.key_state = set()

        self.build_ui()
        self.bind_keyboard()
        self.update_status_text()

        publish_period_ms = max(20, int(1000.0 / self.publish_rate))
        self.root.after(publish_period_ms, self.publish_loop)

        self.get_logger().info(
            f'On-screen joystick publishing /{self.cmd_topic}. '
            'Pad controls translation; turn buttons control yaw.'
        )

    def build_ui(self):
        title = tk.Label(
            self.root,
            text='Wheel-Leg Quadruped',
            bg='#15191d',
            fg='#eef6ff',
            font=('Segoe UI', 18, 'bold'),
        )
        title.pack(pady=(18, 4))

        subtitle = tk.Label(
            self.root,
            text='Pad: forward/back and side-step | Q/E or buttons: rotate',
            bg='#15191d',
            fg='#9fb4c8',
            font=('Segoe UI', 10),
        )
        subtitle.pack(pady=(0, 12))

        self.canvas = tk.Canvas(
            self.root,
            width=self.pad_size,
            height=self.pad_size,
            bg='#15191d',
            highlightthickness=0,
        )
        self.canvas.pack()

        self.draw_pad()
        self.canvas.bind('<ButtonPress-1>', self.on_press)
        self.canvas.bind('<B1-Motion>', self.on_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_release)

        self.status_label = tk.Label(
            self.root,
            text='',
            bg='#15191d',
            fg='#d6f6ff',
            font=('Consolas', 12),
        )
        self.status_label.pack(pady=(14, 10))

        button_frame = tk.Frame(self.root, bg='#15191d')
        button_frame.pack(pady=(0, 8))

        rotate_left_button = tk.Button(
            button_frame,
            text='Turn Left',
            width=12,
            height=2,
            bg='#263849',
            fg='#eef6ff',
            activebackground='#38536b',
            activeforeground='white',
            font=('Segoe UI', 10, 'bold'),
        )
        rotate_left_button.pack(side=tk.LEFT, padx=6)
        rotate_left_button.bind(
            '<ButtonPress-1>',
            lambda event: self.set_command(0.0, 0.0, self.max_angular * 0.68),
        )
        rotate_left_button.bind('<ButtonRelease-1>', lambda event: self.stop_robot())

        stop_button = tk.Button(
            button_frame,
            text='STOP',
            command=self.stop_robot,
            width=12,
            height=2,
            bg='#d84a4a',
            fg='white',
            activebackground='#f05a5a',
            activeforeground='white',
            font=('Segoe UI', 11, 'bold'),
        )
        stop_button.pack(side=tk.LEFT, padx=6)

        rotate_right_button = tk.Button(
            button_frame,
            text='Turn Right',
            width=12,
            height=2,
            bg='#263849',
            fg='#eef6ff',
            activebackground='#38536b',
            activeforeground='white',
            font=('Segoe UI', 10, 'bold'),
        )
        rotate_right_button.pack(side=tk.LEFT, padx=6)
        rotate_right_button.bind(
            '<ButtonPress-1>',
            lambda event: self.set_command(0.0, 0.0, -self.max_angular * 0.68),
        )
        rotate_right_button.bind('<ButtonRelease-1>', lambda event: self.stop_robot())

        close_frame = tk.Frame(self.root, bg='#15191d')
        close_frame.pack(pady=(0, 8))

        close_button = tk.Button(
            close_frame,
            text='Close',
            command=self.close,
            width=12,
            height=2,
            bg='#2a3642',
            fg='#eef6ff',
            activebackground='#38495a',
            activeforeground='white',
            font=('Segoe UI', 11),
        )
        close_button.pack(side=tk.LEFT, padx=8)

        hint = tk.Label(
            self.root,
            text='Keyboard: W/S forward/back, A/D side-step, Q/E rotate, Space stop',
            bg='#15191d',
            fg='#7f95a8',
            font=('Segoe UI', 9),
        )
        hint.pack(pady=(0, 8))

    def draw_pad(self):
        self.canvas.delete('all')

        c = self.center
        r = self.outer_radius
        self.canvas.create_oval(
            c - r,
            c - r,
            c + r,
            c + r,
            fill='#202832',
            outline='#4fd8ff',
            width=4,
        )
        self.canvas.create_oval(
            c - r * 0.62,
            c - r * 0.62,
            c + r * 0.62,
            c + r * 0.62,
            outline='#334657',
            width=2,
        )
        self.canvas.create_line(c, c - r, c, c + r, fill='#334657', width=2)
        self.canvas.create_line(c - r, c, c + r, c, fill='#334657', width=2)

        self.canvas.create_text(c, c - r - 22, text='FORWARD', fill='#d9f8ff')
        self.canvas.create_text(c, c + r + 22, text='REVERSE', fill='#d9f8ff')
        self.canvas.create_text(c - r - 28, c, text='STEP L', fill='#d9f8ff')
        self.canvas.create_text(c + r + 30, c, text='STEP R', fill='#d9f8ff')

        self.knob = self.canvas.create_oval(
            c - self.knob_radius,
            c - self.knob_radius,
            c + self.knob_radius,
            c + self.knob_radius,
            fill='#28d88f',
            outline='#eafff6',
            width=3,
        )
        self.canvas.create_text(
            c,
            c,
            text='DRAG',
            fill='#0a1913',
            font=('Segoe UI', 9, 'bold'),
            tags='knob_text',
        )

    def bind_keyboard(self):
        for key in ('w', 's', 'a', 'd', 'q', 'e'):
            self.root.bind(f'<KeyPress-{key}>', self.on_key_press)
            self.root.bind(f'<KeyRelease-{key}>', self.on_key_release)
        self.root.bind('<space>', lambda event: self.stop_robot())

    def on_press(self, event):
        self.dragging = True
        self.update_from_canvas_point(event.x, event.y)

    def on_drag(self, event):
        if self.dragging:
            self.update_from_canvas_point(event.x, event.y)

    def on_release(self, event):
        self.dragging = False
        self.stop_robot()

    def update_from_canvas_point(self, x, y):
        dx = x - self.center
        dy = y - self.center
        distance = math.hypot(dx, dy)

        if distance > self.outer_radius:
            scale = self.outer_radius / distance
            dx *= scale
            dy *= scale

        # 画面上方代表前进；画面左侧代表向左平移，不再代表转向。
        forward = (-dy / self.outer_radius) * self.max_linear
        lateral = (-dx / self.outer_radius) * self.max_lateral
        self.set_command(forward, lateral, 0.0)
        self.move_knob(self.center + dx, self.center + dy)

    def on_key_press(self, event):
        self.key_state.add(event.keysym.lower())
        self.update_command_from_keys()

    def on_key_release(self, event):
        self.key_state.discard(event.keysym.lower())
        self.update_command_from_keys()

    def update_command_from_keys(self):
        forward = 0.0
        lateral = 0.0
        angular = 0.0

        if 'w' in self.key_state:
            forward += self.max_linear * 0.70
        if 's' in self.key_state:
            forward -= self.max_linear * 0.55
        if 'a' in self.key_state:
            lateral += self.max_lateral * 0.80
        if 'd' in self.key_state:
            lateral -= self.max_lateral * 0.80
        if 'q' in self.key_state:
            angular += self.max_angular * 0.68
        if 'e' in self.key_state:
            angular -= self.max_angular * 0.68

        self.set_command(forward, lateral, angular)

    def set_command(self, linear, lateral, angular):
        self.linear_x = max(-self.max_linear, min(self.max_linear, linear))
        self.linear_y = max(-self.max_lateral, min(self.max_lateral, lateral))
        self.angular_z = max(-self.max_angular, min(self.max_angular, angular))
        self.update_status_text()

    def move_knob(self, x, y):
        self.canvas.coords(
            self.knob,
            x - self.knob_radius,
            y - self.knob_radius,
            x + self.knob_radius,
            y + self.knob_radius,
        )
        self.canvas.coords('knob_text', x, y)

    def stop_robot(self):
        self.linear_x = 0.0
        self.linear_y = 0.0
        self.angular_z = 0.0
        self.key_state.clear()
        self.move_knob(self.center, self.center)
        self.update_status_text()
        self.publish_command()

    def update_status_text(self):
        if hasattr(self, 'status_label'):
            self.status_label.configure(
                text=(
                    f'vx={self.linear_x:+.2f} m/s   '
                    f'vy={self.linear_y:+.2f} m/s   '
                    f'wz={self.angular_z:+.2f} rad/s'
                )
            )

    def publish_loop(self):
        if self.closed:
            return

        self.publish_command()
        self.root.after(max(20, int(1000.0 / self.publish_rate)), self.publish_loop)

    def publish_command(self):
        command = Twist()
        command.linear.x = self.linear_x
        command.linear.y = self.linear_y
        command.angular.z = self.angular_z
        self.publisher.publish(command)

    def close(self):
        self.closed = True
        self.linear_x = 0.0
        self.linear_y = 0.0
        self.angular_z = 0.0
        for _ in range(5):
            self.publish_command()
        self.root.destroy()

    def run(self):
        self.root.mainloop()


def main(args=None):
    rclpy.init(args=args)
    node = OnScreenJoystickNode()

    try:
        node.run()
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
