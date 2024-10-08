import sys
import fitz  # PyMuPDF
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QLabel, QVBoxLayout, QWidget, QScrollArea, QSizePolicy, QPushButton, QHBoxLayout
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen, QColor
from PyQt5.QtCore import Qt, QRect, QPoint

class PDFEditor(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PDF Viewer with Highlighter and Marker")
        self.setGeometry(100, 100, 800, 600)

        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)

        self.layout = QVBoxLayout(self.main_widget)

        # Scroll area for the PDF pages
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.layout.addWidget(self.scroll_area)

        # Page display in QLabel inside a container widget for centering
        self.container_widget = QWidget()
        self.pdf_label = QLabel(self.container_widget)
        
        # Size policy for proper resizing
        self.pdf_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.container_layout = QVBoxLayout(self.container_widget)
        self.container_layout.addWidget(self.pdf_label, alignment=Qt.AlignCenter)
        self.scroll_area.setWidget(self.container_widget)

        # Highlighter and marker buttons
        action_layout = QHBoxLayout()
        self.highlight_button = QPushButton("Highlight", self)
        self.highlight_button.clicked.connect(self.activate_highlighter)
        action_layout.addWidget(self.highlight_button)

        self.marker_button = QPushButton("Marker", self)
        self.marker_button.clicked.connect(self.activate_marker)
        action_layout.addWidget(self.marker_button)

        self.layout.addLayout(action_layout)

        # Initialize variables
        self.pdf_path = None
        self.current_page = 0
        self.doc = None
        self.mode = None  # None, "highlight", or "marker"
        self.mark_start_point = None
        self.rect_start_point = None
        self.current_rect = None

        self.open_pdf()

    def open_pdf(self):
        self.pdf_path, _ = QFileDialog.getOpenFileName(self, "Open PDF", "", "PDF Files (*.pdf)")
        if self.pdf_path:
            self.load_pdf(self.pdf_path)

    def load_pdf(self, pdf_path):
        self.doc = fitz.open(pdf_path)
        self.current_page = 0
        self.load_pdf_page()

    def load_pdf_page(self):
        page = self.doc.load_page(self.current_page)  # Load the current page

        # Convert the page to an image
        pix = page.get_pixmap()
        qimage = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimage)

        self.pdf_label.setPixmap(pixmap)
        self.pdf_label.setFixedSize(pix.width, pix.height)

    def activate_highlighter(self):
        self.mode = "highlight"

    def activate_marker(self):
        self.mode = "marker"

    def mousePressEvent(self, event):
        if self.mode == "marker":
            self.mark_start_point = event.pos()
        elif self.mode == "highlight":
            self.rect_start_point = event.pos()

    def mouseMoveEvent(self, event):
        if self.mode == "marker" and self.mark_start_point:
            painter = QPainter(self.pdf_label.pixmap())
            pen = QPen(Qt.yellow, 3, Qt.SolidLine)  # Set the marker color and thickness
            painter.setPen(pen)
            painter.drawLine(self.mark_start_point, event.pos())
            painter.end()
            self.pdf_label.update()
            self.mark_start_point = event.pos()
        elif self.mode == "highlight" and self.rect_start_point:
            self.current_rect = QRect(self.rect_start_point, event.pos())
            self.update()

    def mouseReleaseEvent(self, event):
        if self.mode == "marker":
            self.mark_start_point = None
        elif self.mode == "highlight" and self.current_rect:
            painter = QPainter(self.pdf_label.pixmap())
            painter.fillRect(self.current_rect, QColor(255, 255, 0, 100))  # Semi-transparent yellow for highlight
            painter.end()
            self.pdf_label.update()
            self.rect_start_point = None
            self.current_rect = None

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:  # Scroll up
            self.prev_page()
        elif event.angleDelta().y() < 0:  # Scroll down
            self.next_page()

    def next_page(self):
        if self.doc and self.current_page < len(self.doc) - 1:
            self.current_page += 1
            self.load_pdf_page()

    def prev_page(self):
        if self.doc and self.current_page > 0:
            self.current_page -= 1
            self.load_pdf_page()

    def paintEvent(self, event):
        if self.mode == "highlight" and self.current_rect:
            painter = QPainter(self)
            painter.setPen(QPen(Qt.yellow, 2, Qt.SolidLine))
            painter.drawRect(self.current_rect)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PDFEditor()
    window.show()
    sys.exit(app.exec_())
