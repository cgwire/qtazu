import os
import logging
import re
import sys
import traceback

import gazu
from Qt import QtWidgets, QtGui, QtCore

log = logging.getLogger(__name__)

KITSU_LOGO = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "res", "image", "logo_kitsu.png"
)


class AnimatedLabel(QtWidgets.QLabel):
    """
    QLabel with animated background color.
    """

    def __init__(self):
        super(AnimatedLabel, self).__init__()
        self.setStyleSheet(
            """
            background-color: #CC4444;
            color: #F5F5F5;
            padding: 5px;
            """
        )
        self.setWordWrap(True)
        self.create_animation()
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                QtWidgets.QSizePolicy.Expanding)

    def create_animation(self):
        """
        Create the animation of the color background.
        """
        color_begin = QtGui.QColor("#943434")
        color_end = QtGui.QColor("#CC4444")
        self.color_anim = QtCore.QPropertyAnimation(self, b"background_color")
        self.color_anim.setStartValue(color_begin)
        self.color_anim.setEndValue(color_end)
        self.color_anim.setDuration(400)

    def start_animation(self):
        """
        Start the animation of the color background.
        """
        self.color_anim.stop()
        self.color_anim.start()

    def get_back_color(self):
        """
        Get the background color.
        """
        return self.palette().color(QtGui.QPalette.Window)

    def set_back_color(self, color):
        """
        Set the given color as background color by parsing the style sheet.
        """
        style = self.styleSheet()
        pattern = "background-color:[^\n;]*"
        new = "background-color: %s" % color.name()
        style = re.sub(pattern, new, style, flags=re.MULTILINE)
        self.setStyleSheet(style)

    # Property to animate : the label background color
    background_color = QtCore.Property(
        QtGui.QColor, get_back_color, set_back_color
    )


class Login(QtWidgets.QDialog):
    """Log-in dialog to CG-Wire"""

    logged_in = QtCore.Signal(bool)

    def __init__(self, parent=None, initialize_host=True):
        super(Login, self).__init__(parent)

        self.setWindowTitle("Connect to Kitsu")

        # Kitsu logo
        logo_label = QtWidgets.QLabel()
        pixmap = QtGui.QPixmap()
        pixmap.load(KITSU_LOGO)
        logo_label.setPixmap(pixmap)
        logo_label.setAlignment(QtCore.Qt.AlignCenter)

        form = QtWidgets.QFormLayout()
        form.setContentsMargins(10, 15, 10, 5)
        form.setObjectName("form")

        # Host
        host_label = QtWidgets.QLabel("Kitsu URL:")
        host_input = QtWidgets.QLineEdit()
        host_input.setPlaceholderText("https://xxx.cg-wire.com/api")

        # User
        user_label = QtWidgets.QLabel("Username:")
        user_input = QtWidgets.QLineEdit()
        user_input.setPlaceholderText("user@host.com")

        # Password
        password_label = QtWidgets.QLabel("Password:")
        password_input = QtWidgets.QLineEdit()
        password_input.setEchoMode(QtWidgets.QLineEdit.Password)

        # Error
        error = AnimatedLabel()
        error.hide()

        # Buttons
        login = QtWidgets.QPushButton("Login")
        login.setAutoDefault(True)
        login.setDefault(True)
        buttons = QtWidgets.QHBoxLayout()
        buttons.addWidget(login)

        form.addRow(host_label, host_input)
        form.addRow(user_label, user_input)
        form.addRow(password_label, password_input)

        self.inputs = dict()
        self.inputs["host"] = host_input
        self.inputs["user"] = user_input
        self.inputs["password"] = password_input
        self.error = error

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(logo_label)
        layout.addLayout(form)
        layout.addWidget(error)
        layout.addLayout(buttons)

        self.resize(325, 160)

        # Connections
        login.clicked.connect(self.on_login)

        if initialize_host:
            # Automatically enter host if available.
            self.initialize_host()

    def show_error(self, message=None):
        """
        Show the error message and emit a failed logged-in signal
        """
        if not message:
            message = (
                "Login verification failed.\n"
                "Please ensure your username and "
                "password are correct."
            )
        self.error.setText(message)
        self.error.show()
        self.error.start_animation()
        self.logged_in.emit(False)

    def initialize_host(self):
        """Initialize host value based on environment"""

        host_input = self.inputs["host"]

        host = os.environ.get("CGWIRE_HOST", None)
        if host is None:
            gazu_host = gazu.client.get_host()
            if gazu_host != "http://gazu.change.serverhost/api":
                # Assume the host in gazu.client is already set correctly
                # and copy it into these settings.
                log.debug(
                    "Setting CG-Wire host from gazu.client: %s" % gazu_host
                )
                host = gazu_host
        else:
            log.debug(
                "Setting CG-Wire host from environment "
                "variable CGWIRE_HOST: %s" % host
            )

        if host:
            # Force the host by environment variable
            host_input.setText(host)
        else:
            host_input.setEnabled(True)

        user_input = self.inputs["user"]
        user_input.setFocus()

    def on_login(self):
        """Perform login with current settings in the dialog."""

        host = self.inputs["host"].text()
        user = self.inputs["user"].text()
        password = self.inputs["password"].text()

        try:
            gazu.set_host(host)
            if not gazu.client.host_is_valid():
                raise gazu.exception.HostException(
                    "Could not connect to the server.\nIs the host URL correct?"
                )
            result = gazu.log_in(user, password)
        except gazu.exception.HostException:
            message = "Could not connect to the server.\nIs the host URL correct?"
            self.show_error(message)
            return
        except gazu.exception.AuthFailedException:
            message = (
                "Login verification failed.\n"
                "Please ensure your username and "
                "password are correct."
            )
            self.show_error(message)
            return
        except Exception:
            # In case of unexpected exception, show the traceback
            message = traceback.format_exc()
            self.show_error(message)
            return

        if result:
            name = "{user[first_name]} {user[last_name]}".format(**result)
            log.info("Logged in as %s.." % name)
            self.logged_in.emit(True)
            self.accept()
        else:
            message = "Unexpected behaviour : Did not retrieve user informations"
            self.show_error(message)