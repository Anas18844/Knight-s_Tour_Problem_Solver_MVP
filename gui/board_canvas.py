import tkinter as tk
from tkinter import Canvas
from typing import List, Tuple, Optional
import math
import os
from PIL import Image, ImageTk


class BoardCanvas(Canvas):
    def __init__(self, parent, board_size: int = 8, cell_size: int = 60, **kwargs):
        self.board_size = board_size
        self.cell_size = cell_size
        self.canvas_size = board_size * cell_size

        super().__init__(parent, width=self.canvas_size, height=self.canvas_size,
                        bg='white', highlightthickness=2, highlightbackground='black',
                        **kwargs)

        # State variables
        self.current_path = []
        self.animation_index = 0
        self.is_animating = False
        self.is_partial_solution = False  # Track if current solution is partial
        self.animation_speed = 200  # milliseconds per step
        self.animation_job = None
        self.selected_start = None
        self.click_callback = None

        # Visual elements
        self.knight_photo = None  # PhotoImage object for knight
        self.knight_pil_image = None  # PIL Image object
        self.path_lines = []
        self.move_numbers = []

        # Load knight image
        self._load_knight_image()

        # Colors
        self.COLOR_LIGHT = '#F0D9B5'
        self.COLOR_DARK = "#A07451"
        self.COLOR_START = '#90EE90'
        self.COLOR_END = '#FFB6C6'
        self.COLOR_PATH = '#4169E1'
        self.COLOR_KNIGHT = '#FF4500'
        self.COLOR_UNVISITED = "#DD6F6F"  # Light red for unvisited cells in partial solutions
        # Draw initial board
        self.draw_board()

        # Bind click event
        self.bind('<Button-1>', self._on_click)

    def _load_knight_image(self):
        """Load and prepare knight image for display."""
        try:
            # Get the path to the knight image (in the project root)
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            knight_image_path = os.path.join(base_path, 'KNIGHT_BLACK.png')

            if os.path.exists(knight_image_path):
                # Load the image using PIL
                self.knight_pil_image = Image.open(knight_image_path)
                # We'll resize it when drawing based on cell size
            else:
                print(f"Warning: Knight image not found at {knight_image_path}")
                self.knight_pil_image = None
        except Exception as e:
            print(f"Error loading knight image: {e}")
            self.knight_pil_image = None

    def draw_board(self):
        """Draw the chessboard pattern."""
        self.delete('all')

        for row in range(self.board_size):
            for col in range(self.board_size):
                x1 = col * self.cell_size
                y1 = row * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                # Alternate colors
                color = self.COLOR_LIGHT if (row + col) % 2 == 0 else self.COLOR_DARK

                # Highlight selected start position
                if self.selected_start == (col, row):
                    color = self.COLOR_START

                self.create_rectangle(x1, y1, x2, y2, fill=color, outline='black',
                                    tags='board')

        # Add coordinate labels
        for i in range(self.board_size):
            # Column labels
            x = i * self.cell_size + self.cell_size // 2
            self.create_text(x, self.canvas_size + 15, text=str(i),font=('Arial', 10, 'bold'), tags='labels')

            # Row labels
            y = i * self.cell_size + self.cell_size // 2
            self.create_text(-15, y, text=str(i),font=('Arial', 10, 'bold'), tags='labels')

    def set_board_size(self, board_size: int):
        self.board_size = board_size
        self.canvas_size = board_size * self.cell_size
        self.config(width=self.canvas_size, height=self.canvas_size)
        self.selected_start = None
        self.clear_animation()
        self.draw_board()

    def _on_click(self, event):
        if self.is_animating:
            return

        # Calculate clicked cell
        col = event.x // self.cell_size
        row = event.y // self.cell_size

        if 0 <= col < self.board_size and 0 <= row < self.board_size:
            self.selected_start = (col, row)
            self.draw_board()

            # Call callback if registered
            if self.click_callback:
                self.click_callback(col, row)

    def set_click_callback(self, callback):
        self.click_callback = callback

    def get_cell_center(self, x: int, y: int) -> Tuple[int, int]:
        pixel_x = x * self.cell_size + self.cell_size // 2
        pixel_y = y * self.cell_size + self.cell_size // 2
        return pixel_x, pixel_y

    def draw_knight(self, x: int, y: int):
        # Remove previous knight
        self.delete('knight')

        center_x, center_y = self.get_cell_center(x, y)

        # Use image if available, otherwise fall back to Unicode symbol
        if self.knight_pil_image is not None:
            try:
                # Calculate size for the knight (80% of cell size for good fit)
                knight_size = int(self.cell_size * 0.8)

                # Resize the knight image
                resized_image = self.knight_pil_image.resize(
                    (knight_size, knight_size),
                    Image.Resampling.LANCZOS
                )

                # Convert to PhotoImage
                self.knight_photo = ImageTk.PhotoImage(resized_image)

                # Draw the image centered on the cell
                self.create_image(center_x, center_y, image=self.knight_photo,
                                tags='knight')
            except Exception as e:
                print(f"Error drawing knight image: {e}")
                # Fall back to Unicode symbol
                self._draw_knight_fallback(center_x, center_y)
        else:
            # Fall back to Unicode symbol
            self._draw_knight_fallback(center_x, center_y)

    def _draw_knight_fallback(self, center_x: int, center_y: int):
        radius = self.cell_size // 3

        # Draw knight as a circle with Unicode knight symbol
        self.create_oval(center_x - radius, center_y - radius,
                        center_x + radius, center_y + radius,
                        fill=self.COLOR_KNIGHT, outline='black', width=2,
                        tags='knight')

        self.create_text(center_x, center_y, text='♞',
                        font=('Arial', self.cell_size // 2, 'bold'),
                        fill='white', tags='knight')

    def draw_path_segment(self, x1: int, y1: int, x2: int, y2: int, move_num: int):
        start_x, start_y = self.get_cell_center(x1, y1)
        end_x, end_y = self.get_cell_center(x2, y2)

        # Draw line
        line = self.create_line(start_x, start_y, end_x, end_y,fill=self.COLOR_PATH, width=3, arrow=tk.LAST,arrowshape=(10, 12, 5), tags='path')
        self.path_lines.append(line)

        # Draw move number at start position
        if move_num > 0:
            num_text = self.create_text(start_x, start_y - self.cell_size // 4,text=str(move_num),font=('Arial', 10, 'bold'),fill='darkred', tags='path_numbers')
            self.move_numbers.append(num_text)

    def highlight_position(self, x: int, y: int, color: str):
        x1 = x * self.cell_size
        y1 = y * self.cell_size
        x2 = x1 + self.cell_size
        y2 = y1 + self.cell_size

        self.create_rectangle(x1, y1, x2, y2, fill=color, outline='black',
                            tags='highlight')

    def highlight_unvisited_cells(self, path: List[Tuple[int, int]]):
        # Create set of visited positions for fast lookup
        visited = set(path)

        # Highlight all unvisited cells
        for row in range(self.board_size):
            for col in range(self.board_size):
                if (row, col) not in visited:
                    self.highlight_position(row, col, self.COLOR_UNVISITED)

    def start_animation(self, path: List[Tuple[int, int]], speed: int = 200,show_full_path: bool = False, is_partial: bool = False):
        self.stop_animation()
        self.clear_animation()

        self.current_path = path
        self.animation_speed = speed
        self.animation_index = 0
        self.is_animating = True
        self.is_partial_solution = is_partial  # Store for use after animation

        if not path:
            return

        # Redraw board
        self.draw_board()

        # If partial solution, highlight unvisited cells first (before animation)
        if is_partial:
            self.highlight_unvisited_cells(path)

        # Highlight start and end positions
        start_x, start_y = path[0]
        self.highlight_position(start_x, start_y, self.COLOR_START)

        if len(path) > 1:
            end_x, end_y = path[-1]
            self.highlight_position(end_x, end_y, self.COLOR_END)

        # If showing full path, draw all segments at once
        if show_full_path:
            for i in range(len(path) - 1):
                x1, y1 = path[i]
                x2, y2 = path[i + 1]
                self.draw_path_segment(x1, y1, x2, y2, i + 1)

            # Draw knight at end
            self.draw_knight(path[-1][0], path[-1][1])
            self.is_animating = False
        else:
            # Start progressive animation
            self._animate_step()

    def _animate_step(self):
        if not self.is_animating or self.animation_index >= len(self.current_path):
            self.is_animating = False
            return

        # Draw current position
        x, y = self.current_path[self.animation_index]
        self.draw_knight(x, y)

        # Draw path segment to next position
        if self.animation_index > 0:
            prev_x, prev_y = self.current_path[self.animation_index - 1]
            self.draw_path_segment(prev_x, prev_y, x, y, self.animation_index)

        self.animation_index += 1

        # Schedule next step
        if self.animation_index < len(self.current_path):
            self.animation_job = self.after(self.animation_speed, self._animate_step)
        else:
            self.is_animating = False

    def stop_animation(self):
        self.is_animating = False
        if self.animation_job:
            self.after_cancel(self.animation_job)
            self.animation_job = None

    def clear_animation(self):
        self.stop_animation()
        self.delete('path')
        self.delete('path_numbers')
        self.delete('knight')
        self.delete('highlight')
        self.path_lines.clear()
        self.move_numbers.clear()
        self.animation_index = 0
        self.current_path = []

    def set_animation_speed(self, speed: int):
        self.animation_speed = max(10, min(2000, speed))

    def show_solution(self, path: List[Tuple[int, int]]):
        self.start_animation(path, show_full_path=True)

    def get_selected_start(self) -> Optional[Tuple[int, int]]:
        return self.selected_start

    def set_selected_start(self, x: int, y: int):
        if 0 <= x < self.board_size and 0 <= y < self.board_size:
            self.selected_start = (x, y)
            self.draw_board()
