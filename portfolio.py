import flet as ft
import flet.canvas as cv
import math
import subprocess
import os

# ── SHARED CONSTANTS ──────────────────────────────────────────────────────────
ACCENT_COLOR   = "#F72578"
DIVIDER_COLOR  = "#C75886"
IC_BADGE       = "#B8326F"
IC_BOOK        = "#9B3A6A"
IC_GROUPS      = "#D94886"
IC_EMAIL       = "#E23674"
IC_PHONE       = "#B73B74"
IC_INSTA       = "#F72578"
TEXT_COLOR     = "#4A1730"
SUBTLE_COLOR = ft.colors.with_opacity(0.78, TEXT_COLOR)
BG_COLOR       = "#F9DCE6"

HEADER_SIZE    = 28
SUBHEADER_SIZE = 20
CONTENT_SIZE   = 14

# ── CONSTELLATION BACKGROUND (built ONCE, reused every page) ──────────────────
def _build_background_shapes():
    shapes = []

    def circle(x, y, radius, color, opacity=1.0):
        shapes.append(cv.Circle(
            x=x, y=y, radius=radius,
            paint=ft.Paint(
                color=ft.colors.with_opacity(opacity, color),
                style=ft.PaintingStyle.FILL,
            ),
        ))

    # Layered side ribbons inspired by the provided reference background.
    side_layers = [
        ("#F72578", 1.00, 430),
        ("#8A2F55", 0.34, 250),
        ("#F94AA4", 0.56, 170),
        ("#B45070", 0.46, 235),
    ]
    for color, opacity, radius in side_layers:
        for y in (-90, 255, 620, 980):
            circle(-90 + radius * 0.15, y, radius, color, opacity)
            circle(1920 + 90 - radius * 0.15, y, radius, color, opacity)

    for offset in (0, 150):
        for y in range(-60, 1140, 320):
            circle(210, y + offset, 110, "#FF5FAE", 0.28)
            circle(1710, y + offset, 110, "#FF5FAE", 0.28)

    wave_paint = ft.Paint(
        color=ft.colors.with_opacity(0.72, "#FFFFFF"),
        stroke_width=2.2,
        style=ft.PaintingStyle.STROKE,
    )
    for side in ("left", "right"):
        base_x = 115 if side == "left" else 1805
        direction = 1 if side == "left" else -1
        for x_offset in (0, 64):
            previous = None
            for step in range(0, 55):
                y = step * 22
                x = base_x + (math.sin(step * 0.42 + x_offset) * 58 + x_offset) * direction
                if previous:
                    shapes.append(cv.Line(
                        x1=previous[0], y1=previous[1], x2=x, y2=y,
                        paint=wave_paint,
                    ))
                previous = (x, y)

    dot_paint = ft.Paint(color=ft.colors.with_opacity(0.76, ACCENT_COLOR))
    for x_start, y_start, scale in ((62, 980, 8), (1520, 910, 8), (1785, 980, 8)):
        for row in range(8):
            for col in range(8 - row // 2):
                shapes.append(cv.Circle(
                    x=x_start + col * scale * 1.8,
                    y=y_start + row * scale * 1.8,
                    radius=2.2,
                    paint=dot_paint,
                ))

    cross_paint = ft.Paint(
        color=ft.colors.with_opacity(0.80, ACCENT_COLOR),
        stroke_width=3,
        style=ft.PaintingStyle.STROKE,
    )
    for x, y in ((360, 470), (360, 540), (1560, 470), (1560, 540)):
        shapes.extend([
            cv.Line(x1=x - 12, y1=y - 12, x2=x + 12, y2=y + 12, paint=cross_paint),
            cv.Line(x1=x + 12, y1=y - 12, x2=x - 12, y2=y + 12, paint=cross_paint),
        ])
    return shapes

# Pre-compute once at import time — all pages share this
_BG_SHAPES = _build_background_shapes()


def build_background():
    return ft.Container(
        expand=True,
        bgcolor=BG_COLOR,
        content=cv.Canvas(expand=True, shapes=_BG_SHAPES),
    )


# ── TOP NAV ───────────────────────────────────────────────────────────────────
def build_top_nav(page: ft.Page, active_key: str):
    def go(route):
        def handler(e):
            page.go(route)
        return handler

    def nav_button(label, icon, route):
        is_active = active_key == route.strip("/")
        return ft.TextButton(
            content=ft.Row(
                [
                    ft.Icon(icon, size=15,
                            color=TEXT_COLOR if is_active else ACCENT_COLOR),
                    ft.Text(label, size=13, weight=ft.FontWeight.W_500,
                            color=TEXT_COLOR if is_active else ACCENT_COLOR),
                ],
                spacing=5,
                tight=True,
            ),
            on_click=go(route),
            style=ft.ButtonStyle(
                padding=ft.Padding(10, 6, 10, 6),
                bgcolor=ft.colors.with_opacity(0.12, ACCENT_COLOR) if is_active
                        else ft.colors.TRANSPARENT,
                overlay_color=ft.colors.with_opacity(0.08, ACCENT_COLOR),
            ),
        )

    return ft.Container(
        bgcolor=ft.colors.with_opacity(0.95, BG_COLOR),
        # ── taller navbar ──
        padding=ft.Padding(20, 14, 20, 14),
        border=ft.border.Border(
            bottom=ft.border.BorderSide(1, ft.colors.with_opacity(0.15, TEXT_COLOR))
        ),
        content=ft.Row(
            controls=[
                # ── UNAM logo replacing text ──
                ft.TextButton(
                    content=ft.Row([
                        ft.Image(
                            src="unam_logo.png",
                            width=70, height=70,
                            fit=ft.BoxFit.CONTAIN,
                            error_content=ft.Text(
                                "UNAM", size=22,
                                weight=ft.FontWeight.BOLD,
                                color=ACCENT_COLOR,
                            ),
                        ),
                        ft.Column([
                            ft.Text("Elina Siwombe", size=14,
                                    weight=ft.FontWeight.BOLD,
                                    color=TEXT_COLOR),
                            ft.Text("Computer Programming I · 2026",
                                    size=10, color=SUBTLE_COLOR),
                        ], spacing=1, tight=True),
                    ], spacing=10, tight=True),
                    on_click=go("/home"),
                    style=ft.ButtonStyle(overlay_color=ft.colors.TRANSPARENT),
                ),
                ft.Row(
                    controls=[
                        nav_button("Home",       ft.Icons.HOME,        "/home"),
                        nav_button("Timeline",   ft.Icons.TIMELINE,    "/timeline"),
                        nav_button("GitHub",     ft.Icons.CODE,        "/github"),
                        nav_button("MATLAB Hub", ft.Icons.SCHOOL,      "/matlab"),
                        nav_button("Demos",      ft.Icons.PLAY_CIRCLE, "/demos"),
                        nav_button("Blog",       ft.Icons.ARTICLE,     "/blog"),
                        nav_button("Contact",    ft.Icons.MAIL,        "/contact"),
                    ],
                    spacing=4,
                    alignment=ft.MainAxisAlignment.END,
                    wrap=True,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )


# ── FULL-PAGE SHELL ───────────────────────────────────────────────────────────
def page_shell(page: ft.Page, active_key: str, body: ft.Control):
    nav = build_top_nav(page, active_key)
    scrollable = ft.Column(
        controls=[
            ft.Container(content=body, padding=ft.Padding(30, 30, 30, 40), expand=True)
        ],
        expand=True,
        scroll=ft.ScrollMode.AUTO,
    )
    page_col = ft.Column(
        controls=[nav, scrollable],
        expand=True,
        spacing=0,
    )
    return ft.Stack(
        controls=[build_background(), page_col],
        expand=True,
    )


# ── HELPER WIDGETS ────────────────────────────────────────────────────────────
def math_module_card(title, description, top_formula,
                     bottom_formula=None, plain_suffix=""):
    formula_controls = []
    if bottom_formula:
        formula_controls += [
            ft.Text(top_formula, size=14, color=ACCENT_COLOR,
                    weight=ft.FontWeight.BOLD),
            ft.Container(width=160, height=1, bgcolor=DIVIDER_COLOR,
                         margin=ft.Margin(top=2, bottom=2)),
            ft.Text(bottom_formula, size=14, color=ACCENT_COLOR,
                    weight=ft.FontWeight.BOLD),
        ]
    else:
        formula_controls.append(
            ft.Text(top_formula, size=14, color=ACCENT_COLOR, italic=True)
        )
    if plain_suffix:
        formula_controls.append(
            ft.Text(plain_suffix, size=12, color=SUBTLE_COLOR)
        )

    return ft.Container(
        content=ft.Column([
            ft.Text(title, size=18, weight=ft.FontWeight.BOLD, color=ACCENT_COLOR),
            ft.Text(description, size=CONTENT_SIZE, color=TEXT_COLOR),
            ft.Container(
                content=ft.Column(
                    formula_controls,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                padding=12,
                bgcolor=ft.colors.with_opacity(0.15, BG_COLOR),
                border=ft.border.all(1, ft.colors.with_opacity(0.10, TEXT_COLOR)),
                border_radius=6,
            ),
        ], spacing=10),
        padding=20,
        border=ft.border.all(1, ft.colors.with_opacity(0.12, TEXT_COLOR)),
        border_radius=10,
        col={"sm": 12, "md": 6, "lg": 4},
    )


def blog_post_preview(title, description):
    return ft.Container(
        content=ft.Column([
            ft.Text(title, size=SUBHEADER_SIZE,
                    weight=ft.FontWeight.BOLD, color=ACCENT_COLOR),
            ft.Text(description, size=CONTENT_SIZE, color=TEXT_COLOR),
            ft.TextButton("Read full post…",
                          style=ft.ButtonStyle(color=ACCENT_COLOR)),
        ], spacing=5),
        margin=ft.Margin(bottom=20),
        padding=15,
        border=ft.border.all(1, ft.colors.with_opacity(0.12, TEXT_COLOR)),
        border_radius=10,
    )


def cert_card(img_path):
    return ft.Container(
        content=ft.Image(src=img_path, border_radius=10, fit=ft.BoxFit.COVER),
        padding=10,
        bgcolor="#FFFFFF",
        border_radius=15,
        shadow=ft.BoxShadow(blur_radius=10,
                            color=ft.colors.with_opacity(0.26, ft.colors.BLACK)),
        col={"sm": 12, "md": 6},
    )


def skill_chip(label, icon, color):
    return ft.Container(
        content=ft.Row([
            ft.Icon(icon, size=16, color=color),
            ft.Text(label, size=13, color=TEXT_COLOR,
                    weight=ft.FontWeight.W_500),
        ], spacing=6, tight=True),
        padding=ft.Padding(12, 8, 12, 8),
        border=ft.border.all(1, ft.colors.with_opacity(0.25, color)),
        border_radius=20,
        bgcolor=ft.colors.with_opacity(0.08, color),
    )


# ══════════════════════════════════════════════════════════════════════════════
# PAGE BODIES
# ══════════════════════════════════════════════════════════════════════════════

# ── HOME ──────────────────────────────────────────────────────────────────────
def home_body():
    profile_section = ft.ResponsiveRow(
        controls=[
            ft.Container(
                col={"sm": 12, "md": 5},
                content=ft.Container(
                    width=280, height=340,
                    border_radius=20,
                    border=ft.border.all(1, ft.colors.with_opacity(0.3, ACCENT_COLOR)),
                    padding=10,
                    content=ft.Image(src="Gladys.jpeg", fit=ft.BoxFit.COVER,
                                     border_radius=14),
                ),
            ),
            ft.Container(
                col={"sm": 12, "md": 7},
                padding=ft.Padding(left=15, right=15, top=10, bottom=10),
                content=ft.Column(
                    spacing=15,
                    controls=[
                        ft.Column(spacing=4, controls=[
                            ft.Text("Elina Siwombe M", size=36,
                                    weight=ft.FontWeight.BOLD,
                                    color=TEXT_COLOR),
                            ft.Text("Civil Engineering Student | Lead Developer",
                                    size=16, color=ACCENT_COLOR,
                                    weight=ft.FontWeight.W_500),
                        ]),
                        ft.Divider(color=DIVIDER_COLOR, height=10, thickness=1),
                        ft.Column(spacing=8, controls=[
                            ft.Text("Project Brief", size=18,
                                    weight=ft.FontWeight.BOLD,
                                    color=TEXT_COLOR),
                            ft.Text(
                                "Serving as the Lead Developer for Group 15 in the "
                                "Mobile App Development For Computer Programming I, "
                                "I managed the software implementation lifecycle for "
                                "MechTek—our cross-platform Machine Fault Reporting "
                                "System built using Expo, React Native, and Firebase.",
                                size=15, color=SUBTLE_COLOR,
                            ),
                        ]),
                        ft.Column(spacing=5, controls=[
                            ft.Row([
                                ft.Icon(ft.Icons.BADGE, color=IC_BADGE, size=16),
                                ft.Text("Student Number: 225150522",
                                        size=14, color=SUBTLE_COLOR),
                            ]),
                            ft.Row([
                                ft.Icon(ft.Icons.BOOK_ROUNDED, color=IC_BOOK, size=16),
                                ft.Text("Module: Computer Programming I",
                                        size=14, color=SUBTLE_COLOR),
                            ]),
                            ft.Row([
                                ft.Icon(ft.Icons.GROUPS_3, color=IC_GROUPS, size=16),
                                ft.Text("Assigned Team: Group 15 (MechTek)",
                                        size=14, color=SUBTLE_COLOR),
                            ]),
                        ]),
                    ],
                ),
            ),
            
        ],
        spacing=30,
        run_spacing=30,
    )

    # ── SKILLS & TECH SECTION (the area indicated in the image) ──
    skills_section = ft.Container(
        margin=ft.Margin(top=40, bottom=0, left=0, right=0),
        content=ft.Column([
            ft.Row([
                ft.Container(
                    width=4, height=30, bgcolor=ACCENT_COLOR,
                    border_radius=2,
                    margin=ft.Margin(right=12, top=0, left=0, bottom=0),
                ),
                ft.Text("Skills & Technologies",
                        size=SUBHEADER_SIZE + 2,
                        weight=ft.FontWeight.BOLD,
                        color=TEXT_COLOR),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Container(height=6),
            ft.Text(
                "A snapshot of the tools, frameworks, and languages I apply across "
                "the MechTek project and my academic coursework at UNAM.",
                size=CONTENT_SIZE, color=SUBTLE_COLOR,
            ),
            ft.Container(height=18),

            # Row 1 — Languages
            ft.Text("Languages", size=13, color=ACCENT_COLOR,
                    weight=ft.FontWeight.W_600),
            ft.Container(height=6),
            ft.Row(wrap=True, spacing=10, run_spacing=10, controls=[
                skill_chip("Python",      ft.Icons.CODE,            "#5BC8F5"),
                skill_chip("JavaScript",  ft.Icons.JAVASCRIPT,      "#FACC15"),
                skill_chip("JSX / React", ft.Icons.WIDGETS,         "#A78BFA"),
                skill_chip("MATLAB",      ft.Icons.CALCULATE,       "#4ADE80"),
            ]),
            ft.Container(height=16),

            # Row 2 — Frameworks & Tools
            ft.Text("Frameworks & Tools", size=13, color=ACCENT_COLOR,
                    weight=ft.FontWeight.W_600),
            ft.Container(height=6),
            ft.Row(wrap=True, spacing=10, run_spacing=10, controls=[
                skill_chip("Flet",          ft.Icons.DESKTOP_WINDOWS, "#5BC8F5"),
                skill_chip("React Native",  ft.Icons.PHONE_ANDROID,   "#F472B6"),
                skill_chip("Expo",          ft.Icons.ROCKET_LAUNCH,   "#FB923C"),
                skill_chip("Firebase",      ft.Icons.LOCAL_FIRE_DEPARTMENT, "#FACC15"),
                skill_chip("AsyncStorage",  ft.Icons.CLOUD_SYNC,      "#34D399"),
                skill_chip("Git & GitHub",  ft.Icons.MERGE_TYPE,      "#F87171"),
            ]),
            ft.Container(height=16),

            # Row 3 — Engineering domains
            ft.Text("Engineering Domains", size=13, color=ACCENT_COLOR,
                    weight=ft.FontWeight.W_600),
            ft.Container(height=6),
            ft.Row(wrap=True, spacing=10, run_spacing=10, controls=[
                skill_chip("Civil Engineering",        ft.Icons.DOMAIN,          "#A78BFA"),
                skill_chip("Asset Fault Tracking",     ft.Icons.BUILD_CIRCLE,    "#4ADE80"),
                skill_chip("NoSQL / Firestore",        ft.Icons.STORAGE,         "#5BC8F5"),
                skill_chip("System Architecture",      ft.Icons.ACCOUNT_TREE,    "#FB923C"),
                skill_chip("Cross-Platform Dev",       ft.Icons.DEVICES,         "#F472B6"),
            ]),

            ft.Container(height=30),
            ft.Divider(color=DIVIDER_COLOR, thickness=1),

            # Quick-stats bar
            ft.Container(height=10),
            ft.ResponsiveRow(
                controls=[
                    _stat_card("8",   "MATLAB Courses",   ft.Icons.SCHOOL,           "#4ADE80"),
                    _stat_card("15%", "CA Weighting",     ft.Icons.GRADE,            "#FACC15"),
                    _stat_card("16",  "Team Members",     ft.Icons.GROUPS_3,         "#F472B6"),
                    _stat_card("5",   "Sprint Phases",    ft.Icons.TIMELINE,         "#5BC8F5"),
                ],
                spacing=15, run_spacing=15,
            ),
        ]),
        padding=ft.Padding(30, 28, 30, 28),
        border=ft.border.all(1, ft.colors.with_opacity(0.12, TEXT_COLOR)),
        border_radius=14,
        bgcolor=ft.colors.with_opacity(0.06, TEXT_COLOR),
    )

    return ft.Column(
        expand=True,
        controls=[
            profile_section, 
            skills_section,
            ft.Container(expand=True),
            ft.Divider(color=DIVIDER_COLOR, height=60),
            ft.Column(
                [
                    ft.Text(
                        "© 2026 Elina Siwombe | Mobile App Development For Computer Programming ",
                        color=SUBTLE_COLOR,
                        size=12, italic=True,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                width=float("inf"),
            ),
            ft.Container(height=20),
        ], 
        spacing=0
    )



def _stat_card(value, label, icon, color):
    return ft.Container(
        col={"xs": 6, "sm": 6, "md": 3},
        content=ft.Column([
            ft.Icon(icon, size=28, color=color),
            ft.Text(value, size=32, weight=ft.FontWeight.BOLD,
                    color=TEXT_COLOR),
            ft.Text(label, size=12, color=SUBTLE_COLOR,
                    text_align=ft.TextAlign.CENTER),
        ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=4,
        ),
        padding=20,
        border=ft.border.all(1, ft.colors.with_opacity(0.15, color)),
        border_radius=12,
        bgcolor=ft.colors.with_opacity(0.07, color),
    )


# ── TIMELINE ─────────────────────────────────────────────────────────────────
def timeline_body():
    entries = [
        ("Weeks 1–2: Initiation & Architecture",
         "Conducted initial design meetings to finalize the SRS technical contracts, "
         "role-based access flows, and data boundaries.",
         ft.Icons.ASSIGNMENT_TURNED_IN, "#5BC8F5", "SRS ARCHITECTURE"),
        ("Weeks 3–5: UI/UX & Frontend Scaffolding",
         "Collaborated with design leads to engineer modular components, form handling "
         "states, and responsive view containers matching mobile dimensions.",
         ft.Icons.DASHBOARD_CUSTOMIZE, "#A78BFA", "UI COMPONENTS"),
        ("Weeks 6–8: Core Route & Navigation Engineering",
         "Constructed state routing arrays, layout switching flows, and contextual "
         "tracking views for workers, technicians, and supervisors.",
         ft.Icons.ALT_ROUTE, "#4ADE80", "ROUTING MATRIX"),
        ("Weeks 9–10: Optimization & Offline Queue Strategy",
         "Configured system performance parameters, component rendering optimizations, "
         "and AsyncStorage local data fallback setups.",
         ft.Icons.CLOUD_SYNC, "#FB923C", "ASYNC STORAGE"),
        ("Weeks 11–12+: Deployment & Quality Assurance",
         "Assisted with end-to-end connectivity verification, Firestore document rule "
         "testing, and production behavior QA against SRS system benchmarks.",
         ft.Icons.VERIFIED, "#F472B6", "PRODUCTION QA"),
    ]

    cards = [
        ft.Container(
            padding=20,
            margin=ft.Margin(bottom=15, top=0, left=0, right=0),
            border=ft.border.all(1, ft.colors.with_opacity(0.15, TEXT_COLOR)),
            border_radius=12,
            bgcolor=ft.colors.with_opacity(0.08, TEXT_COLOR),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[
                    ft.Container(
                        content=ft.Icon(icon_node, color=node_color, size=24),
                        margin=ft.Margin(right=10, top=2, left=0, bottom=0),
                    ),
                    ft.Column(expand=True, spacing=8, controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Text(title, size=18,
                                        weight=ft.FontWeight.BOLD, color=ACCENT_COLOR),
                                ft.Container(
                                    content=ft.Text(badge_text, size=11,
                                                    color=BG_COLOR,
                                                    weight=ft.FontWeight.W_600),
                                    bgcolor=ft.colors.with_opacity(0.80, ACCENT_COLOR),
                                    padding=10, border_radius=15,
                                ),
                            ],
                        ),
                        ft.Text(desc, size=CONTENT_SIZE, color=SUBTLE_COLOR),
                    ]),
                ],
            ),
        )
        
        for title, desc, icon_node, node_color, badge_text in entries
    ]

    return ft.Column(controls=[
        ft.Text("Project Timeline", size=HEADER_SIZE,
                weight=ft.FontWeight.BOLD, color=TEXT_COLOR),
        ft.Container(
            content=ft.Text(
                "As the Lead Developer of Group 15, I spearheaded the technical "
                "development of MechTek. My primary responsibility involved constructing "
                "system architecture boundaries, implementing secure front-to-back "
                "workflows with Firebase, and turning core SRS functional specifications "
                "into cross-platform code modules.",
                size=CONTENT_SIZE, color=SUBTLE_COLOR,
            ),
            margin=ft.Margin(bottom=25, top=10),
        ),
        
        *cards,
        ft.Divider(color=DIVIDER_COLOR, height=60),
        ft.Column(
            [
                ft.Text(
                    "© 2026 Elina Siwombe | Mobile App Development For Computer Programming ",
                    color=SUBTLE_COLOR,
                    size=12, italic=True,
                    text_align=ft.TextAlign.CENTER, # Ensures multi-line text wraps centered
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            width=float("inf"), # Forces the alignment container to span the full window width
        ),
        ft.Container(height=20),

    ], spacing=0)


# ── GITHUB ────────────────────────────────────────────────────────────────────
def github_body():
    return ft.Column(controls=[
        ft.Text("GitHub Evidence & Documentation", size=HEADER_SIZE,
                weight=ft.FontWeight.BOLD, color=TEXT_COLOR),
        ft.Container(
            content=ft.Text(
                "Working alongside our GitHub Managers, I pushed structural baseline "
                "revisions, engineered major routing blocks, and resolved script merge "
                "constraints. Our workflow utilised descriptive branching schemas to "
                "track functional progress dynamically against academic criteria.",
                size=CONTENT_SIZE, color=SUBTLE_COLOR,
            ),
            margin=ft.Margin(bottom=20, top=10),
        ),
        ft.Container(
            content=ft.Column([
                ft.Text("Mining Engineering Module Impact Summary",
                        size=SUBHEADER_SIZE, weight=ft.FontWeight.BOLD,
                        color=ACCENT_COLOR),
                ft.Text(
                    "Problem Statement: The structural asset registries for Mining "
                    "infrastructure facilities were suffering transaction synchronization "
                    "blockages over standard network connections.\n\n"
                    "Individual Resolution: I engineered a local asynchronous payload "
                    "boundary buffer utilising AsyncStorage. By capturing system faults "
                    "instantly at the device line, structural engineers can report asset "
                    "distress metrics without active cell signals, ensuring zero record "
                    "dropouts across mining operations.",
                    size=CONTENT_SIZE, color=TEXT_COLOR,
                ),
            ]),
            padding=20,
            bgcolor=ft.colors.with_opacity(0.10, TEXT_COLOR),
            border_radius=10,
            margin=ft.Margin(bottom=20),
        ),
        ft.Divider(height=10, thickness=1,
                   color=ft.colors.with_opacity(0.12, TEXT_COLOR)),
        ft.Text("Project Repository", size=SUBHEADER_SIZE,
                weight=ft.FontWeight.BOLD, color=TEXT_COLOR),
        ft.Container(
            content=ft.ElevatedButton(
                "View Production Repository on GitHub",
                icon=ft.Icons.CODE,
                style=ft.ButtonStyle(
                    color=BG_COLOR, bgcolor=ACCENT_COLOR,
                    padding=20,
                    shape=ft.RoundedRectangleBorder(radius=8),
                ),
                url="https://github.com/224032909/MechTek.git",
            ),
            padding=ft.Padding(left=40, right=40),
        ),
        ft.Container(height=20),
        ft.Text("Verifiable Pull Request & Code Review Logs",
                size=SUBHEADER_SIZE, weight=ft.FontWeight.BOLD, color=TEXT_COLOR),
        ft.ResponsiveRow([
            ft.Container(
                content=ft.Column(controls=[
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.CALL_MERGE, color="green"),
                        title=ft.Text("PR #12: Local Async Storage Layer",
                                      color=TEXT_COLOR,
                                      weight=ft.FontWeight.BOLD),
                        subtitle=ft.Text(
                            "Merged 'feature/async-storage' into main",
                            color=ACCENT_COLOR),
                    ),
                    ft.Container(
                        content=ft.Image(src="github_contr.png",
                                         border_radius=4, fit=ft.BoxFit.COVER),
                        padding=ft.Padding(left=16, right=16, bottom=16),
                    ),
                ], spacing=0),
                col={"sm": 12, "md": 6},
                bgcolor=ft.colors.with_opacity(0.10, TEXT_COLOR),
                border_radius=8,
            ),
            ft.Container(
                content=ft.Column(controls=[
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.RATE_REVIEW, color="amber"),
                        title=ft.Text("Feature: Report Fault Screen Layout",
                                      color=TEXT_COLOR,
                                      weight=ft.FontWeight.BOLD),
                        subtitle=ft.Text(
                            "Fixed formatting in ReportFaultScreen.jsx",
                            color=ACCENT_COLOR),
                    ),
                    ft.Container(
                        content=ft.Image(src="portfolio.png", height=200,
                                         border_radius=4, fit=ft.BoxFit.COVER),
                        padding=ft.Padding(left=16, right=16, bottom=16),
                    ),
                ], spacing=0),
                col={"sm": 12, "md": 6},
                bgcolor=ft.colors.with_opacity(0.10, TEXT_COLOR),
                border_radius=8,
            ),
        ], spacing=15),
        ft.Container(height=15),
        ft.Container(
            content=ft.Column(controls=[
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.HISTORY, color="blue"),
                    title=ft.Text("Development Commit History Screenshots",
                                  color=TEXT_COLOR, weight=ft.FontWeight.BOLD),
                    subtitle=ft.Text(
                        "Chronological stream of verified code repository updates",
                        color=ACCENT_COLOR),
                ),
                ft.Container(
                    content=ft.Image(src="history.png",
                                     border_radius=4, fit=ft.BoxFit.COVER),
                    padding=ft.Padding(left=16, right=16, bottom=16),
                ),
            ], spacing=0),
            bgcolor=ft.colors.with_opacity(0.10, TEXT_COLOR),
            border_radius=8,
        ),
        ft.Divider(color=DIVIDER_COLOR, height=60),
        ft.Column(
            [
                ft.Text(
                    "© 2026 Elina Siwombe | Mobile App Development For Computer Programming ",
                    color=SUBTLE_COLOR,
                    size=12, italic=True,
                    text_align=ft.TextAlign.CENTER, # Ensures multi-line text wraps centered
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            width=float("inf"), # Forces the alignment container to span the full window width
        ),
        ft.Container(height=20),

    ], spacing=10)


# ── MATLAB ────────────────────────────────────────────────────────────────────
def matlab_body():
    images = [
        "matlab1.png", "matlab2.png", "matlab3.png", "matlab4.png",
        "matlab5.png", "matlab6.png", "matlab7.png", "matlab8.png",
    ]
    labels = {
        "matlab1.png": "Plot Beyond the Second Dimension",
        "matlab2.png": "Calculations with Vectors and Matrices",
        "matlab3.png": "MATLAB Onramp",
        "matlab4.png": "Simulink Onramp",
        "matlab5.png": "Explore Data with MATLAB Plots",
        "matlab6.png": "Core MATLAB Skills",
        "matlab7.png": "Make and Manipulate Matrices",
        "matlab8.png": "MATLAB Desktop Tools and Troubleshooting Scripts",
    }

    return ft.Column(controls=[
        ft.Text("MATLAB Academic Hub", size=HEADER_SIZE,
                weight=ft.FontWeight.BOLD, color=TEXT_COLOR),
        ft.Container(
            content=ft.Text(
                "Verified course completions from the MathWorks Learning Center. "
                "All 8 self-paced certificates were earned as part of the Computer "
                "Programming I module requirements for Semester 1, 2026.",
                size=CONTENT_SIZE, color=SUBTLE_COLOR,
            ),
            margin=ft.Margin(bottom=20, top=10),
        ),
        ft.ResponsiveRow(
            controls=[
                ft.Container(
                    col={"xs": 12, "sm": 6, "md": 3},
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8,
                        controls=[
                            cert_card(img),
                            ft.Text(labels.get(img, "MATLAB Course"),
                                    size=14, weight=ft.FontWeight.W_500,
                                    color=TEXT_COLOR,
                                    text_align=ft.TextAlign.CENTER),
                        ],
                    ),
                )
                for img in images
            ],
            spacing=10, run_spacing=20,
        ),
        ft.Divider(color=DIVIDER_COLOR, height=60),
        ft.Column(
            [
                ft.Text(
                    "© 2026 Elina Siwombe | Mobile App Development For Computer Programming ",
                    color=SUBTLE_COLOR,
                    size=12, italic=True,
                    text_align=ft.TextAlign.CENTER, # Ensures multi-line text wraps centered
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            width=float("inf"), # Forces the alignment container to span the full window width
        ),
        ft.Container(height=20),

    ])


# ── DEMOS ─────────────────────────────────────────────────────────────────────
def demos_body():
    return ft.Column(
        controls=[
            ft.Column(
                [
                    ft.Text("MechTek System Demonstrations", size=HEADER_SIZE,
                            weight=ft.FontWeight.W_800, color=TEXT_COLOR,
                            style=ft.TextStyle(letter_spacing=0.5)),
                    # Changed color to a lighter, readable golden-tinted white
                    ft.Text("Interactive media updates and core logic validations.", size=14, color=ft.colors.with_opacity(0.7, TEXT_COLOR)),
                ],
                spacing=4,
            ),
            ft.Container(
                width=float("inf"),
                height=260,
                gradient=ft.LinearGradient(
                    begin=ft.Alignment(-1.0, -1.0),
                    end=ft.Alignment(1.0, 1.0),
                    colors=["#FFD7E4", "#F72578"],
                ),
                # Replaced harsh white border with a very subtle bronze-gold border that matches the theme
                border=ft.border.all(1, ft.colors.with_opacity(0.12, ACCENT_COLOR)),
                border_radius=16,
                padding=24,
                content=ft.Row(
                    [
                        ft.Column(
                            [
                                ft.Container(
                                    content=ft.Text("VIDEO RESOURCE", size=10, weight="bold", color=ACCENT_COLOR),
                                    bgcolor=ft.colors.with_opacity(0.1, ACCENT_COLOR),
                                    padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                                    border_radius=20,
                                ),
                                ft.Text("Play MechTek Demo Video", color=TEXT_COLOR, size=20, weight="bold"),
                                # Changed color to a crisp, readable opaque tone instead of the dark blue-gray
                                ft.Text("Review system data processing architecture pipelines live.", color=ft.colors.with_opacity(0.6, TEXT_COLOR), size=13),
                                ft.Container(expand=True),
                                ft.ElevatedButton(
                                    content=ft.Row(
                                        [
                                            ft.Icon(ft.Icons.PLAY_ARROW_ROUNDED, color=BG_COLOR),
                                            ft.Text("Click here to Watch my project contribution video", color=BG_COLOR, weight="bold"),
                                        ],
                                        spacing=8,
                                    ),
                                    style=ft.ButtonStyle(
                                        bgcolor=ACCENT_COLOR,
                                        shape=ft.RoundedRectangleBorder(radius=8),
                                        padding=ft.Padding.symmetric(horizontal=20, vertical=12)
                                    ),
                                    on_click=lambda e: subprocess.Popen(["start", "https://1drv.ms/v/c/c445a73c8b31892f/IQD7XacAqCNDSI9vZ1sl5si0AYtQNSvc3wn-wZN8RhLHtJ4?e=zRfw7D"], shell=True),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.START,
                            expand=True,
                            spacing=8,
                        ),
                        ft.Container(
                            content=ft.Icon(ft.Icons.PLAY_CIRCLE_FILLED_ROUNDED, size=80, color=ACCENT_COLOR),
                            alignment=ft.Alignment(0.0, 0.0),
                            expand=True,
                        ),
                    ],
                ),
            ),
            ft.Container(
                padding=ft.Padding.symmetric(vertical=10),
                content=ft.Divider(height=1, color=ft.colors.with_opacity(0.08, TEXT_COLOR))
            ),
            ft.Text("Confidence in Concepts: System Mathematics",
                    size=SUBHEADER_SIZE, weight=ft.FontWeight.W_700, color=TEXT_COLOR),
            ft.ResponsiveRow(
                [
                    math_module_card(
                        "Fault Lifecycle Workflow",
                        "Digitization and systematic progression tracking of structural asset breakdowns.",
                        "Status Lifecycle: Reported → Repairing → Fixed",
                    ),
                    math_module_card(
                        "Mean Time To Repair (MTTR)",
                        "Firestore real-time telemetry metrics tracking engineering repair turnarounds.",
                        "MTTR = [ ∑ⁿᵢ₌₁ (Maintenance_Timeᵢ) ] / N",
                        "N = Total Number of Fixed Assets",
                        "Notation Compliant Formula Model",
                    ),
                    math_module_card(
                        "Asset Status Indexing",
                        "Dynamic relational data mapping connecting machinery profiles with filed failure reports.",
                        "Condition Mapping: Active || Faulty || Under_Repair",
                    ),
                    math_module_card(
                        "Operational Financial Model",
                        "Formula model verifying aggregate materials processing costs matching lecture criterion.",
                        "Total Cost = ∑ⁿᵢ₌₁ (Qᵢ × Pᵢ) + Overheads",
                        None,
                        "Aggregate Procurement Value Contract",
                    ),
                ],
                spacing=24,
                run_spacing=24,
            ),
            
            ft.Divider(color=DIVIDER_COLOR, height=60),
            ft.Column(
                [
                    ft.Text(
                        "© 2026 Elina Siwombe | Mobile App Development For Computer Programming",
                        color=SUBTLE_COLOR,
                        size=12, italic=True,
                        text_align=ft.TextAlign.CENTER, # Ensures multi-line text wraps centered
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                width=float("inf"), # Forces the alignment container to span the full window width
            ),
            ft.Container(height=20),

        ],
        spacing=24,
    )


# ── BLOG ──────────────────────────────────────────────────────────────────────
def blog_post_preview(title: str, body: str):
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(title, size=18, weight=ft.FontWeight.BOLD, color=TEXT_COLOR),
                ft.Container(height=8),
                ft.Text(body, size=CONTENT_SIZE, color=SUBTLE_COLOR),
            ]
        ),
        padding=ft.Padding(left=0, right=0, top=16, bottom=24),
        border=ft.Border(bottom=ft.BorderSide(1, DIVIDER_COLOR)),
    )


# ── BLOG ──────────────────────────────────────────────────────────────────────
def blog_post_preview(title: str, body: str):
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(title, size=18, weight=ft.FontWeight.BOLD, color=ACCENT_COLOR),
                ft.Container(height=8),
                ft.Text(body, size=CONTENT_SIZE, color=SUBTLE_COLOR),
            ]
        ),
        padding=ft.Padding(left=0, right=0, top=20, bottom=28),
        border=ft.Border(bottom=ft.BorderSide(1, DIVIDER_COLOR)),
        margin=ft.Margin(bottom=4, top=0, left=0, right=0),
    )


def blog_body():
    return ft.Column(controls=[
        ft.Text("Technical Engineering Blog", size=HEADER_SIZE,
                weight=ft.FontWeight.BOLD, color=TEXT_COLOR),
        ft.Container(
            content=ft.Text(
                "A sequence of design analyses explaining our methodologies, "
                "implementation roadmaps, and optimization milestones completed "
                "during the development of MechTek for the University of Namibia.",
                size=CONTENT_SIZE, color=SUBTLE_COLOR,
            ),
            margin=ft.Margin(bottom=30, top=10),
        ),

        blog_post_preview(
            "Cross-Platform Performance and React Native",
            "MechTek is built on Expo and React Native — a deliberate architectural choice "
            "driven by the realities of industrial mobile deployment. In mining and heavy "
            "manufacturing environments, maintenance teams operate across a fragmented device "
            "landscape, from entry-level Android handsets to mid-range Samsung Galaxy units. "
            "A managed Expo workflow eliminates native build complexity, granting the team unified "
            "access to camera APIs, file system utilities, and push notification infrastructure "
            "without maintaining separate Android and iOS codebases. Performance targets are "
            "non-negotiable: the main dashboard must render within three seconds on a 10 Mbps "
            "connection, list scrolling must sustain 60 fps, and the total app binary must remain "
            "under 50 MB. These constraints shaped every component decision — from lazy-loaded "
            "fault lists to compressed media previews — ensuring MechTek remains fast and reliable "
            "even on aging hardware in noisy, dusty industrial sites across Namibia.",
        ),

        blog_post_preview(
            "Structuring NoSQL Document Boundaries in Firestore",
            "Designing a Firestore schema for a role-stratified maintenance system required "
            "rethinking relational database instincts from the ground up. MechTek organises "
            "data across three primary collections — users, machines, and faults — each with "
            "tightly scoped access patterns enforced through Firebase Security Rules. Workers "
            "may only read and write their own fault documents; technicians access faults "
            "assigned to them and can push status transitions from 'Repairing' to 'Fixed'; "
            "supervisors hold full read-write authority across all collections. Machine records "
            "carry an enum status field ('active', 'faulty', 'repairing') that updates in real "
            "time as faults progress through the lifecycle, giving supervisors a live operational "
            "picture without polling. The permission matrix was stress-tested with unauthenticated "
            "client calls to confirm that every read and write operation requires a valid "
            "request.auth token — a hard security requirement baked into Firestore rules rather "
            "than application-layer logic, preventing privilege escalation at the database level.",
        ),

        blog_post_preview(
            "Mitigating Information Loss in Remote Industrial Operations",
            "One of the most critical reliability challenges in MechTek's domain is intermittent "
            "connectivity. Underground mining operations and remote industrial sites frequently lose "
            "network coverage entirely, yet a breakdown report delayed by hours can translate directly "
            "into significant lost productivity. MechTek addresses this through an AsyncStorage offline "
            "queue: when a fault submission is triggered without an active connection, the structured "
            "report data is serialised and persisted locally on the device. On reconnection, an automatic "
            "synchronisation boundary resolves the queue against Firestore, with exponential backoff "
            "retries guarding against flaky network handshakes. The system enforces a clear offline "
            "constraint boundary — media uploads require an active connection due to Firebase Storage "
            "limitations — but all structured fault metadata survives without data loss. Reliability "
            "acceptance criteria mandate a 100% offline-to-online sync rate, verified by a controlled "
            "test: disable network, submit a report, force-close the app, reopen on restored "
            "connectivity, and confirm the fault document appears correctly in Firestore.",
        ),

        blog_post_preview(
            "Role-Based Access Control and Authentication Architecture",
            "MechTek enforces a strict three-tier role model — Worker, Technician, and Supervisor — "
            "implemented through Firebase Authentication combined with Firestore user profile documents. "
            "On registration, each user is assigned a role enum stored in their Firestore user record, "
            "which governs every data access pattern in the system. Workers submit fault reports and "
            "track status; technicians view their assigned workload and update repair progress; "
            "supervisors assign technicians, monitor all active faults, and access performance analytics. "
            "Security rules prevent any role from escalating its own privileges by ensuring role "
            "modifications require supervisor-level auth tokens. Firebase Auth handles all password "
            "hashing server-side, meaning no plaintext credentials are ever stored in Firestore or "
            "AsyncStorage. Sessions persist across app restarts, eliminating repeated logins for field "
            "workers operating in time-pressured environments, while still requiring an initial online "
            "authentication before offline mode can activate — a deliberate tradeoff protecting data "
            "integrity across the entire fault management lifecycle.",
        ),

        blog_post_preview(
            "Media Handling, Compression, and Firebase Storage Strategy",
            "Fault reports in industrial maintenance are significantly more actionable when accompanied "
            "by photographic or video evidence of the breakdown. MechTek integrates Expo's ImagePicker "
            "APIs to allow workers to capture or select media directly from their device, which is then "
            "uploaded to Firebase Storage under paths scoped to the user's authenticated ID — preventing "
            "cross-user access at the storage layer. Because MechTek targets Android devices operating "
            "on the Firebase Storage free tier (limited to 5 GB), images exceeding 1 MB are compressed "
            "before upload to balance visual quality against storage budget consumption. The system "
            "enforces a clear constraint: media uploads require an active network connection and cannot "
            "be queued offline, as binary payloads cannot be reliably held in AsyncStorage. Upload "
            "performance is benchmarked against a 10-second completion target for files over 1 MB, "
            "measured on standard Wi-Fi. All storage URLs are written back into the corresponding "
            "Firestore fault document as an array field, keeping media references tightly coupled "
            "to fault records and ensuring supervisors and technicians retrieve the correct evidence "
            "without any manual linking step.",
        ),

        ft.Column(
            [
                ft.Text(
                    "© 2026 Elina Siwombe | Mobile App Development For Computer Programming",
                    color=SUBTLE_COLOR,
                    size=12, italic=True,
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            width=float("inf"),
        ),
        ft.Container(height=20),
    ])


# ── CONTACT ───────────────────────────────────────────────────────────────────
def contact_body(page: ft.Page):
    name_field  = ft.TextField(label="Name",    border_color=ACCENT_COLOR,
                                color=TEXT_COLOR, cursor_color=ACCENT_COLOR)
    email_field = ft.TextField(label="Email",   border_color=ACCENT_COLOR,
                                color=TEXT_COLOR)
    msg_field   = ft.TextField(label="Message", multiline=True, min_lines=3,
                                border_color=ACCENT_COLOR, color=TEXT_COLOR)

    return ft.Column(controls=[
        ft.Text("Contact Me", size=32, weight=ft.FontWeight.BOLD,
                color=TEXT_COLOR),
        ft.Container(
            padding=20,
            content=ft.ResponsiveRow(
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        col={"sm": 12, "md": 6},
                        padding=20,
                        content=ft.Column([
                            ft.Text(
                                "I am always open to new academic collaborations, "
                                "development opportunities, or discussions surrounding "
                                "industrial asset tracking and civil system structures. "
                                "Drop me a message below to connect!",
                                size=16, color=TEXT_COLOR,
                                text_align=ft.TextAlign.LEFT,
                            ),
                            ft.Container(height=15),
                            ft.Column([
                                ft.Row([
                                    ft.Icon(ft.Icons.EMAIL, color=IC_EMAIL, size=18),
                                    ft.Text("Email: ", weight=ft.FontWeight.BOLD,
                                            color=TEXT_COLOR, size=15),
                                    ft.Text("elinaglady@gmail.com",
                                            color=SUBTLE_COLOR, size=15),
                                ], spacing=5),
                                ft.Row([
                                    ft.Icon(ft.Icons.PHONE, color=IC_PHONE, size=18),
                                    ft.Text("Cell: ", weight=ft.FontWeight.BOLD,
                                            color=TEXT_COLOR, size=15),
                                    ft.Text("+264 81 4823549",
                                            color=SUBTLE_COLOR, size=15),
                                ], spacing=5),
                                ft.Row([
                                    ft.Icon(ft.Icons.CAMERA_ALT, color=IC_INSTA, size=18),
                                    ft.Text("Instagram: ", weight=ft.FontWeight.BOLD,
                                            color=TEXT_COLOR, size=15),
                                    ft.Text("_glady.s_",
                                            color=SUBTLE_COLOR, size=15),
                                ], spacing=5),
                            ], spacing=10),
                        ])
                    ),
                    ft.Container(
                        col={"sm": 12, "md": 5},
                        padding=30,
                        bgcolor=ft.colors.with_opacity(0.12, ACCENT_COLOR),
                        border=ft.border.all(
                            1, ft.colors.with_opacity(0.12, TEXT_COLOR)),
                        border_radius=20,
                        content=ft.Column(
                            spacing=15,
                            controls=[
                                name_field, email_field, msg_field,
                                ft.ElevatedButton(
                                    "Send Message",
                                    style=ft.ButtonStyle(bgcolor=DIVIDER_COLOR,
                                                         color=BG_COLOR),
                                    width=float("inf"),
                                    on_click=lambda _: page.launch_url(
                                        f"mailto:elinaglady@gmail.com"
                                        f"?subject=Message from {name_field.value}"
                                        f"&body=From: {email_field.value}"
                                        f"%0D%0A%0D%0A{msg_field.value}"
                                    ),
                                ),
                            ],
                        ),
                    ),
                ],
            ),
        ),
        ft.Divider(color=DIVIDER_COLOR, height=60),
        ft.Column(
            [
                ft.Text(
                    "© 2026 Elina Siwombe | Mobile App Development For Computer Programming",
                    color=SUBTLE_COLOR,
                    size=12, italic=True,
                    text_align=ft.TextAlign.CENTER, # Ensures multi-line text wraps centered
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            width=float("inf"), # Forces the alignment container to span the full window width
        ),
        ft.Container(height=20),

    ])


# ══════════════════════════════════════════════════════════════════════════════
# ROUTER
# ══════════════════════════════════════════════════════════════════════════════
def main(page: ft.Page):
    page.title = "Web Portfolio — Elina Siwombe M"
    page.assets_dir = "./assets"
    page.padding = 0
    page.scroll = "none"
    page.bgcolor = BG_COLOR

    def route_change(e):
        page.controls.clear()
        route = page.route or "/home"

        route_map = {
            "/home":     ("home",     home_body()),
            "/timeline": ("timeline", timeline_body()),
            "/github":   ("github",   github_body()),
            "/matlab":   ("matlab",   matlab_body()),
            "/demos":    ("demos",    demos_body()),
            "/blog":     ("blog",     blog_body()),
            "/contact":  ("contact",  contact_body(page)),
        }

        key, body = route_map.get(route, route_map["/home"])
        page.add(page_shell(page, key, body))
        page.update()

    page.on_route_change = route_change
    page.go("/home")


ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=int(os.environ.get("PORT", 8080)))
