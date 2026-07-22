import fitz  # PyMuPDF
from PIL import Image
import io

class LazyPDFReader:
    def __init__(self, pdf_path, view_width=800, view_height=480):
        """
        Initializes the lazy PDF reader.
        
        :param pdf_path: Path to the PDF file.
        :param view_width: Target width of the returned image.
        :param view_height: Target height of the returned image.
        """
        self.doc = fitz.open(pdf_path)
        self.total_pages = len(self.doc)
        
        self.view_width = view_width
        self.view_height = view_height
        self.aspect_ratio = view_width / view_height
        
        self.current_page_idx = 0
        self.current_y_offset = 0  # Track vertical position within the current page
        
        # Internal cache for the currently open page's dimensions and scaling
        self._current_page = None
        self._page_height_scaled = 0
        self._load_page(0)

    def _load_page(self, page_idx):
        """Helper to load a page and calculate how many vertical steps it needs."""
        if 0 <= page_idx < self.total_pages:
            self.current_page_idx = page_idx
            self._current_page = self.doc[page_idx]
            
            # Get original dimensions
            rect = self._current_page.rect
            orig_width = rect.width
            orig_height = rect.height
            
            # Calculate scale factor to make the page width match our view_width
            self.scale = self.view_width / orig_width
            self._page_height_scaled = orig_height * self.scale
            
            # Reset vertical offset to the top of the new page
            self.current_y_offset = 0

    def _render_current_view(self):
        """Renders the current 800x480 viewport window into a PIL Image."""
        # Convert our scaled target window back to the PDF's original coordinate system
        inv_scale = 1.0 / self.scale
        
        x0 = 0
        y0 = self.current_y_offset * inv_scale
        x1 = self.view_width * inv_scale
        y1 = (self.current_y_offset + self.view_height) * inv_scale
        
        # Create a matrix to scale the output to our exact pixel dimensions
        matrix = fitz.Matrix(self.scale, self.scale)
        
        # Clip the rendering area to just our current viewport window
        clip_rect = fitz.Rect(x0, y0, x1, y1)
        pix = self._current_page.get_pixmap(matrix=matrix, clip=clip_rect)
        
        # Convert PyMuPDF pixmap data cleanly into a PIL Image
        img_data = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_data))
        
        # If we reached the absolute bottom of a page, the clip might be shorter than 480px.
        # We pad it with white so the returned image is strictly 800x480.
        if img.size != (self.view_width, self.view_height):
            padded_img = Image.new("RGB", (self.view_width, self.view_height), "white")
            padded_img.paste(img, (0, 0))
            return padded_img
            
        return img

    def go_to_page(self, page_num):
        """Jumps directly to a 0-indexed page number."""
        if 0 <= page_num < self.total_pages:
            self._load_page(page_num)
        return self._render_current_view()

    def next_view(self):
        """
        Moves down by one viewport height. If it hits the bottom of the page,
        it automatically rolls over to the top of the next page.
        """
        max_y = self._page_height_scaled - self.view_height
        
        # If we can still scroll down on this page
        if self.current_y_offset < max_y:
            # Scroll down by one full viewport height, but don't overshoot the page bottom
            self.current_y_offset = min(self.current_y_offset + self.view_height, max_y)
        else:
            # We are at the bottom, go to the next page
            if self.current_page_idx + 1 < self.total_pages:
                self._load_page(self.current_page_idx + 1)
                
        return self._render_current_view()

    def previous_view(self):
        """
        Moves up by one viewport height. If it hits the top of the page,
        it rolls back to the bottom view of the previous page.
        """
        if self.current_y_offset > 0:
            # Scroll up, but don't overshoot the top
            self.current_y_offset = max(self.current_y_offset - self.view_height, 0)
        else:
            # We are at the top, go to the previous page's bottom view
            if self.current_page_idx > 0:
                self._load_page(self.current_page_idx - 1)
                # Set offset to the absolute bottom view of this prior page
                max_y = max(0, self._page_height_scaled - self.view_height)
                self.current_y_offset = max_y
                
        return self._render_current_view()

    def next_page(self):
        """Jumps straight to the top of the next page."""
        if self.current_page_idx + 1 < self.total_pages:
            self._load_page(self.current_page_idx + 1)
        return self._render_current_view()

    def previous_page(self):
        """Jumps straight to the top of the previous page."""
        if self.current_page_idx > 0:
            self._load_page(self.current_page_idx - 1)
        return self._render_current_view()
