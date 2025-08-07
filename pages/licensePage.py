import logging
import requests
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QWidget, QMessageBox
from PyQt6.QtGui import QFont, QFontDatabase
from ui.license_ui import Ui_Form
from features.license_manage import view_license, create_or_update_license, remove_all_files
from features.data_save_signals import signals
from models import Session, Notification
import firebase_admin
from firebase_admin import credentials, firestore

# Configure logger
logging.basicConfig(
    filename="license.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Config constants
ACCESS_TOKEN = "KtJgRk8shkc9gTtMZfHAmfpwy8gnREuj"
RESET_MODE = "Unlimited"
CREDIT = 0
PRICE = 50
PLAN = "Lifetime"
EXPIRY = "Never"

# Initialize Firebase Admin
try:
    cred = credentials.Certificate("firebase-adminsdk.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    logger.info("Firebase initialized successfully.")
except Exception as e:
    logger.error(f"Failed to initialize Firebase: {e}")

class licensePage(QWidget):
    def __init__(self, username=None):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.username = username
        self.session = Session()

        self.setup_fonts()
        self.setup_ui()
        signals.license_saved.connect(self.setup_ui)


    def setup_fonts(self):
        try:
            font_bold_id = QFontDatabase.addApplicationFont("font/Inter_18pt-Bold.ttf")
            font_regular_id = QFontDatabase.addApplicationFont("font/OpenSans-Regular.ttf")

            font_bold = QFont(QFontDatabase.applicationFontFamilies(font_bold_id)[0], 13)
            font_regular = QFont(QFontDatabase.applicationFontFamilies(font_regular_id)[0], 11)

            self.apply_font_to_all_widgets(font_regular)
            self.apply_fonts_by_object_names(font_bold, ["label"])
        except Exception as e:
            logger.warning(f"Font setup failed: {e}")

    def apply_font_to_all_widgets(self, font):
        for widget in self.findChildren(QWidget):
            widget.setFont(font)

    def apply_fonts_by_object_names(self, font, object_names):
        for name in object_names:
            widget = self.findChild(QWidget, name)
            if widget:
                widget.setFont(font)

    def setup_ui(self):
        self.ui.error.setText("")
        self.ui.sucess.setText("")
        self.ui.license_key.setText("")
        data = view_license()

        if data:
            self.ui.license_status.setText("Activated")
            self.ui.exp_date_status.setText(data.get('expiry', 'N/A'))
            self.ui.last_activate_time.setText(data.get('activate_time', 'N/A'))
            self.ui.price.setText('$' + str(data.get('price', 0)))
            self.ui.license_hide_lebel.show()
            self.ui.remove_license.show()
        else:
            self.ui.license_hide_lebel.hide()
            self.ui.remove_license.hide()
            self.ui.license_status.setText("Not Activated")
            self.ui.exp_date_status.setText("N/A")
            self.ui.last_activate_time.setText("N/A")
            self.ui.price.setText('$0')


        try:
            self.ui.update_license.clicked.disconnect()
        except Exception:
            pass

        try:
            self.ui.remove_license.clicked.disconnect()
        except Exception:
            pass
        self.ui.update_license.clicked.connect(self.update_license)
        self.ui.remove_license.clicked.connect(self.remove_license)

    def update_license(self):
        license_key = self.ui.license_key.text().strip()
        self.ui.error.setText("")
        self.ui.sucess.setText("")

        if not license_key:
            self.show_message("Please input a valid Purchase Code.", error=True)
            self.ui.error.setText("Please input a valid Purchase Code.")
            return

        self.ui.error.setText("Please wait...")
        self.ui.update_license.setEnabled(False)
        QtWidgets.QApplication.processEvents()

        try:
            headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
            response = requests.get(f"https://api.envato.com/v3/market/author/sale?code={license_key}", headers=headers)

            doc_ref = db.collection("purchase_codes").document(license_key)

            if response.status_code == 403:
                doc = doc_ref.get()
                if doc.exists:
                    self.ui.error.setText("Purchase Code already in use.")
                else:
                    doc_ref.set({"used": True})
                    create_or_update_license(license_key, PRICE, CREDIT, PLAN, EXPIRY, RESET_MODE)
                    self.show_success("Purchase Code successfully updated.")

            elif response.status_code == 200:
                doc_ref.set({"used": True})
                create_or_update_license(license_key, PRICE, CREDIT, PLAN, EXPIRY, RESET_MODE)
                self.show_success("Purchase Code successfully updated.")

            else:
                self.ui.error.setText("Invalid or Not Found Purchase Code.")

        except Exception as e:
            self.ui.error.setText(f"Error updating Purchase Code: {str(e)}")
            logger.exception("Exception occurred during license update.")
        finally:
            self.ui.update_license.setEnabled(True)

    def remove_license(self):
        self.ui.error.setText("")
        self.ui.sucess.setText("")

        license_data = view_license()
        if not license_data:
            self.ui.error.setText("No active license to remove.")
            return

        purchase_code = license_data.get("license")
        try:
            db.collection("purchase_codes").document(purchase_code).delete()
            remove_all_files()

            self.setup_ui()
            self.ui.sucess.setText("License removed.")
            Notification.add_notification(self.session, "Purchase Code removed.")
        except Exception as e:
            self.ui.error.setText(f"Error removing Purchase Code: {str(e)}")
            logger.exception("Exception during license removal")

        self.ui.sucess.setText("License removed.")
        self.ui.error.setText("")
        Notification.add_notification(self.session, "Purchase Code removed.")
        self.setup_ui()  # << This forces UI to reset state


    def show_message(self, message, error=False):
        title = "Error" if error else "Info"
        QMessageBox.information(self, title, message)
        logger.info(f"Message shown to user: {title} - {message}")

    def show_success(self, message):
        self.ui.sucess.setText(message)
        self.ui.license_key.setText("")
        Notification.add_notification(self.session, message)
        self.setup_ui()
