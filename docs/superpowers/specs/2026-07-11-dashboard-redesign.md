# Dashboard Redesign — School Library Management System

## Scope

UI-only redesign of three files: `main_window.py` (sidebar + top bar), `theme.py` (new reusable widgets), and `dashboard.py` (full rewrite). Zero changes to business logic, database, services, validations, or navigation behavior.

## Files to modify

| File | Changes |
|------|---------|
| `ui/main_window.py` | Sidebar recolored to dark navy `#071C43`, Unicode icons on nav items, decorative bottom panel. Top bar redesigned with white bg, search placeholder, notification icon + badge, school/date display. |
| `ui/theme.py` | Add `DashboardCard`, `ActionButton`, `StatusBadge`, `DonutChart` (QPainter), `LineChart` (QPainter) reusable widgets. |
| `ui/dashboard.py` | Full rewrite. Keeps `refresh()` + `report_service` calls identical. New layout: welcome → stat cards → quick actions → tables → bottom row. |

## Color palette

- Sidebar bg: `#071C43`
- Sidebar hover/active: `#246BFD` to `#1556D8`
- Page bg: `#F6F9FE`
- Card bg: `#FFFFFF`
- Primary text: `#10234A`
- Secondary text: `#6B7894`
- Borders: `#E3EAF5`
- Accents: blue `#246BFD`, green `#22B96B`, orange `#FF9800`, red `#EF4444`, purple `#7657F6`, cyan `#16A9D5`

## Sidebar (main_window.py)

- Fixed 240px width, dark navy `#071C43`
- Logo (56px) centered
- "School Library" title, "Management System" subtitle
- Decorative divider
- Nav items with Unicode icons (e.g. ◆ Dashboard, 📚 Books), white text, rounded active state with blue gradient
- Spacer, then "Library Assistant" info card (decorative, no logic)
- "Version 1.0" at bottom

## Top bar (main_window.py)

- White bg, fixed height ~56px
- Left: search-style field with placeholder "Search books, students, issues..." (visual-only)
- Right: notification bell icon + small red badge, school logo thumbnail, "DVNS · School Library" text + dropdown arrow + date

## Dashboard (dashboard.py) — layout top→bottom

1. **Welcome area**: "Welcome back! 📚" heading, "Here's what's happening..." subtitle, date card on right
2. **Stat cards row**: 8 cards (Total Books, Available, Issued, Students, Pending Returns, Overdue, Low Stock, Quick Actions). Icon circle + label + value + description.
3. **Quick Actions**: 2×2 grid inside the 8th card slot — Issue Book, Return Book, Add Book, Add Student. Each with icon + label. Connected to existing `main_window.navigate()`.
4. **Tables row**: "Recent Issues" (Student, Book, Issue Date, Due Date, Status) + "Recent Returns" (Student, Book, Issue Date, Return Date). White card, light header, colored status badges, View All button.
5. **Bottom row**: Donut chart (Available/Issued/Total books from existing `dashboard_summary()`), "Monthly Issue Trend" (shows "No monthly trend data available" — no source data exists), Notice Board (static — Library Timings, Return Reminder text).

## Status badge colors (table)

- ISSUED → green `#22B96B`
- RETURNED → blue `#246BFD`
- OVERDUE → red `#EF4444`
- LOST/DAMAGED → orange `#FF9800`
- Others → grey

## Data sources (unchanged)

- `report_service.dashboard_summary()` → stat card values
- `report_service.recent_issues(8)` → issues table
- `report_service.recent_returns(8)` → returns table
- `report_service.dashboard_summary()` → donut chart values
- `utils.format_display_date()`, `utils.today_str()` → date display
- Navigation via `main_window.navigate()` for quick actions

## What is NOT implemented (no source data)

- Monthly trend line chart — shows fallback text
- Notice board — shows static library-hours text
- Notification dropdown — visual bell icon only
- Profile dropdown — visual arrow only
- Search functionality — visual-only field

## Verification

1. Dashboard opens without errors
2. Stat values match pre-redesign
3. All 7 nav items work (sidebar buttons)
4. Quick action buttons navigate correctly
5. Issues/returns tables load real data
6. No database or service code changed
