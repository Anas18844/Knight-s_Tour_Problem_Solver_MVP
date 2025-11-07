"""Board canvas for visualizing Knight's Tour with animation."""

import tkinter as tk
from tkinter import Canvas
from typing import List, Tuple, Optional
import math


class BoardCanvas(Canvas):
    """
    Custom Canvas widget for displaying and animating Knight's Tour solutions.

    Features:
    - Chessboard visualization
    - Step-by-step knight movement animation
    - Click-to-select starting position
    - Animation speed control
    """

    def __init__(self, parent, board_size: int = 8, cell_size: int = 60, **kwargs):
        """
        Initialize board canvas.

        Args:
            parent: Parent widget
            board_size: Size of the board (n x n)
            cell_size: Size of each cell in pixels
            **kwargs: Additional canvas options
        """
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
        self.animation_speed = 200  # milliseconds per step
        self.animation_job = None
        self.selected_start = None
        self.click_callback = None

        # Visual elements
        self.knight_image = None
        self.path_lines = []
        self.move_numbers = []

        # Colors
        self.COLOR_LIGHT = '#F0D9B5'
        self.COLOR_DARK = '#B58863'
        self.COLOR_START = '#90EE90'
        self.COLOR_END = '#FFB6C6'
        self.COLOR_PATH = '#4169E1'
        self.COLOR_KNIGHT = '#FF4500'

        # Draw initial board
        self.draw_board()

        # Bind click event
        self.bind('<Button-1>', self._on_click)

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
            self.create_text(x, self.canvas_size + 15, text=str(i),
                           font=('Arial', 10, 'bold'), tags='labels')

            # Row labels
            y = i * self.cell_size + self.cell_size // 2
            self.create_text(-15, y, text=str(i),
                           font=('Arial', 10, 'bold'), tags='labels')

    def set_board_size(self, board_size: int):
        """
        Update board size.

        Args:
            board_size: New board size
        """
        self.board_size = board_size
        self.canvas_size = board_size * self.cell_size
        self.config(width=self.canvas_size, height=self.canvas_size)
        self.selected_start = None
        self.clear_animation()
        self.draw_board()

    def _on_click(self, event):
        """Handle click event to select starting position."""
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
        """Set callback function for cell clicks."""
        self.click_callback = callback

    def get_cell_center(self, x: int, y: int) -> Tuple[int, int]:
        """
        Get pixel coordinates of cell center.

        Args:
            x: Column index
            y: Row index

        Returns:
            Tuple of (pixel_x, pixel_y)
        """
        pixel_x = x * self.cell_size + self.cell_size // 2
        pixel_y = y * self.cell_size + self.cell_size // 2
        return pixel_x, pixel_y

    def draw_knight(self, x: int, y: int):
        """
        Draw knight at specified position.

        Args:
            x: Column index
            y: Row index
        """
        # Remove previous knight
        self.delete('knight')

        center_x, center_y = self.get_cell_center(x, y)
        radius = self.cell_size // 3

        # Draw knight as a circle with "K"
        self.create_oval(center_x - radius, center_y - radius,
                        center_x + radius, center_y + radius,
                        fill=self.COLOR_KNIGHT, outline='black', width=2,
                        tags='knight')

        self.create_text(center_x, center_y, text='♞',
                        font=('Arial', self.cell_size // 2, 'bold'),
                        fill='white', tags='knight')

    def draw_path_segment(self, x1: int, y1: int, x2: int, y2: int, move_num: int):
        """
        Draw a path segment with arrow.

        Args:
            x1, y1: Start position
            x2, y2: End position
            move_num: Move number
        """
        start_x, start_y = self.get_cell_center(x1, y1)
        end_x, end_y = self.get_cell_center(x2, y2)

        # Draw line
        line = self.create_line(start_x, start_y, end_x, end_y,
                               fill=self.COLOR_PATH, width=3, arrow=tk.LAST,
                               arrowshape=(10, 12, 5), tags='path')
        self.path_lines.append(line)

        # Draw move number at start position
        if move_num > 0:
            num_text = self.create_text(start_x, start_y - self.cell_size // 4,
                                       text=str(move_num),
                                       font=('Arial', 10, 'bold'),
                                       fill='darkred', tags='path_numbers')
            self.move_numbers.append(num_text)

    def highlight_position(self, x: int, y: int, color: str):
        """
        Highlight a specific position.

        Args:
            x: Column index
            y: Row index
            color: Highlight color
        """
        x1 = x * self.cell_size
        y1 = y * self.cell_size
        x2 = x1 + self.cell_size
        y2 = y1 + self.cell_size

        self.create_rectangle(x1, y1, x2, y2, fill=color, outline='black',
                            tags='highlight')

    def start_animation(self, path: List[Tuple[int, int]], speed: int = 200,
                       show_full_path: bool = False):
        """
        Start animating knight's tour.

        Args:
            path: List of (x, y) coordinates
            speed: Animation speed in milliseconds per step
            show_full_path: If True, show complete path; if False, show progressively
        """
        self.stop_animation()
        self.clear_animation()

        self.current_path = path
        self.animation_speed = speed
        self.animation_index = 0
        self.is_animating = True

        if not path:
            return

        # Redraw board
        self.draw_board()

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
        """Animate one step of the knight's tour."""
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
        """Stop current animation."""
        self.is_animating = False
        if self.animation_job:
            self.after_cancel(self.animation_job)
            self.animation_job = None

    def clear_animation(self):
        """Clear all animation elements."""
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
        """
        Set animation speed.

        Args:
            speed: Delay in milliseconds per step
        """
        self.animation_speed = max(10, min(2000, speed))

    def show_solution(self, path: List[Tuple[int, int]]):
        """
        Display complete solution without animation.

        Args:
            path: List of (x, y) coordinates
        """
        self.start_animation(path, show_full_path=True)

    def get_selected_start(self) -> Optional[Tuple[int, int]]:
        """
        Get currently selected starting position.

        Returns:
            Tuple of (x, y) or None if not selected
        """
        return self.selected_start

    def set_selected_start(self, x: int, y: int):
        """
        Programmatically set starting position.

        Args:
            x: Column index
            y: Row index
        """
        if 0 <= x < self.board_size and 0 <= y < self.board_size:
            self.selected_start = (x, y)
            self.draw_board()
