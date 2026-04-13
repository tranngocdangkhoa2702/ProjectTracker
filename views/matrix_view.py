import customtkinter as ctk


class MatrixView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        ctk.CTkLabel(self, text="📊 MA TRẬN EISENHOWER (Phân loại)", font=("Arial", 22, "bold")).pack(pady=20,
                                                                                                     anchor="w",
                                                                                                     padx=20)

        # Grid layout cho 4 ô ma trận
        matrix_container = ctk.CTkFrame(self, fg_color="transparent")
        matrix_container.pack(fill="both", expand=True, padx=20, pady=10)

        # Ô 1: Khẩn cấp & Quan trọng (P1)
        q1 = ctk.CTkFrame(matrix_container, fg_color="#441a1a", border_width=2, border_color="#c0392b")
        q1.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        ctk.CTkLabel(q1, text="DO FIRST (P1)\nKhẩn & Quan trọng", text_color="#e74c3c",
                     font=("Arial", 16, "bold")).pack(pady=10)
        ctk.CTkTextbox(q1, height=150, fg_color="transparent").pack(fill="both", expand=True, padx=5)

        # Ô 2: Không khẩn & Quan trọng (P2)
        q2 = ctk.CTkFrame(matrix_container, fg_color="#1a2b1a", border_width=2, border_color="#27ae60")
        q2.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        ctk.CTkLabel(q2, text="SCHEDULE (P2)\nKhông khẩn & Quan trọng", text_color="#2ecc71",
                     font=("Arial", 16, "bold")).pack(pady=10)
        ctk.CTkTextbox(q2, height=150, fg_color="transparent").pack(fill="both", expand=True, padx=5)

        # Ô 3: Khẩn cấp & Không quan trọng (P3)
        q3 = ctk.CTkFrame(matrix_container, fg_color="#3e3e1a", border_width=2, border_color="#f1c40f")
        q3.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        ctk.CTkLabel(q3, text="DELEGATE (P3)\nKhẩn & Không quan trọng", text_color="#f39c12",
                     font=("Arial", 16, "bold")).pack(pady=10)

        # Ô 4: Không khẩn & Không quan trọng (P4)
        q4 = ctk.CTkFrame(matrix_container, fg_color="#2c2c2c", border_width=2, border_color="#7f8c8d")
        q4.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        ctk.CTkLabel(q4, text="DELETE (P4)\nKhông khẩn & Không quan trọng", text_color="#95a5a6",
                     font=("Arial", 16, "bold")).pack(pady=10)

        # Cấu hình grid để các ô giãn đều
        matrix_container.grid_columnconfigure((0, 1), weight=1)
        matrix_container.grid_rowconfigure((0, 1), weight=1)