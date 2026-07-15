# School Library Management System — Design Document

## 1. Document Purpose

This `design.md` file defines the visual design, layout structure, UI components, user experience rules, and interaction behavior for the **School Library Management System** desktop application.

The goal is to create a clean, simple, professional, and practical desktop interface for a school librarian.

The application should be easy to use even for non-technical school staff.

---

## 2. Product Design Goal

The design goal is to build an offline desktop application that feels:

- Simple
- Clean
- Professional
- Fast
- Reliable
- Easy to understand
- Suitable for daily school library use

The librarian should be able to perform common tasks quickly:

- Add books
- Add students
- Issue books
- Return books
- Search records
- View pending returns
- Export reports to Excel

The design should avoid unnecessary complexity.

---

## 3. Target Users

## Primary User

### Admin / Librarian

The main user is the school librarian or office staff member who manages library records.

The user may not be highly technical, so the design must be:

- Clear
- Button-driven
- Easy to navigate
- Form-based
- Error-proof
- Comfortable for daily use

---

## 4. Design Principles

## 4.1 Simplicity First

The interface should be simple and direct.

Avoid:

- Too many nested menus
- Complex settings
- Hidden actions
- Overloaded screens
- Technical database terms

Use clear labels such as:

```text
Add Book
Issue Book
Return Book
Export to Excel
Pending Returns
```

---

## 4.2 Dashboard-First Experience

After opening the app, the librarian should land on the Dashboard.

The Dashboard should show the current library status at a glance:

- Total books
- Available books
- Issued books
- Students
- Pending returns
- Overdue books
- Low-stock books

---

## 4.3 Fast Daily Actions

The most common actions should be visible and easy to access.

Important actions:

- Add Book
- Add Student
- Issue Book
- Return Book
- Search Book
- Export Report

These actions should be available with clear buttons.

---

## 4.4 Safe Data Handling

The UI should prevent mistakes.

Examples:

- Disable Issue button when available quantity is 0.
- Show confirmation before deleting or deactivating.
- Show warning when student already has the same book.
- Prevent returning the same issue record twice.
- Prefer deactivate instead of permanent delete.

---

## 4.5 Consistent Layout

Every page should follow the same structure:

```text
Page Title
Short description
Action buttons
Search/filter area
Main table/form
Status messages
```

This makes the application easier to learn.

---

## 5. Recommended UI Technology

## Preferred Option: PySide6

PySide6 is recommended for a professional desktop application.

### Why PySide6 is Good for This Design

| Reason | Benefit |
|---|---|
| Modern desktop UI | Looks professional |
| Strong table support | Good for books, students, and reports |
| Form widgets | Easy to create data entry screens |
| Styling support | Can use Qt stylesheets |
| Scalable | Better for future upgrades |
| Packaging support | Can be converted to `.exe` |

---

## 6. Alternative UI Technology

## Tkinter / CustomTkinter

Tkinter can be used if the app needs to be very simple.

CustomTkinter can improve the look of Tkinter.

### When to Use Tkinter

Use Tkinter if:

- Budget is low.
- UI needs are basic.
- The client wants a very simple application.
- Development should be faster.

### When to Use PySide6

Use PySide6 if:

- The client wants a better-looking application.
- The app needs tables, filters, and reports.
- The project should feel professional.
- Future expansion is expected.

---

## 7. Visual Style

## 7.1 Overall Look

The application should have a clean school-office style.

Recommended visual direction:

- Light theme
- White or off-white background
- Blue or green primary color
- Soft gray borders
- Clear table layout
- Rounded buttons
- Simple icons
- Professional spacing

---

## 7.2 Color Palette

Recommended color palette:

| Usage | Color | Hex |
|---|---|---|
| Primary | School Blue | `#2563EB` |
| Primary Hover | Dark Blue | `#1D4ED8` |
| Secondary | Green | `#16A34A` |
| Warning | Orange | `#F59E0B` |
| Danger | Red | `#DC2626` |
| Success | Green | `#22C55E` |
| Background | Light Gray | `#F8FAFC` |
| Surface/Card | White | `#FFFFFF` |
| Border | Soft Gray | `#E5E7EB` |
| Text Primary | Dark Gray | `#111827` |
| Text Secondary | Medium Gray | `#6B7280` |

### Color Usage

| Element | Color |
|---|---|
| Main buttons | Primary blue |
| Success messages | Green |
| Warning messages | Orange |
| Delete/deactivate buttons | Red |
| Cards | White |
| Page background | Light gray |
| Table borders | Soft gray |

---

## 7.3 Typography

Use a clean readable font.

Recommended fonts:

| Use | Font |
|---|---|
| Headings | Segoe UI / Inter / Arial |
| Body text | Segoe UI / Inter / Arial |
| Tables | Segoe UI / Arial |
| Buttons | Segoe UI Semibold |

### Font Sizes

| Element | Size |
|---|---|
| App title | 20px - 24px |
| Page title | 22px - 26px |
| Section title | 16px - 18px |
| Body text | 13px - 15px |
| Table text | 12px - 14px |
| Button text | 13px - 15px |
| Small helper text | 11px - 12px |

---

## 8. Application Layout

## 8.1 Main Window Layout

Recommended desktop layout:

```text
+------------------------------------------------------+
| Top Bar: School Library Management System            |
+----------------------+-------------------------------+
| Sidebar Navigation   | Main Content Area             |
|                      |                               |
| Dashboard            | Page Title                    |
| Books Management     | Search / Filters / Actions    |
| Student Management   | Table / Form / Report         |
| Issue Book           |                               |
| Return Book          |                               |
| Reports              |                               |
| Settings             |                               |
+----------------------+-------------------------------+
```

---

## 8.2 Window Size

Recommended minimum size:

```text
Width: 1100px
Height: 700px
```

The app should also work reasonably on:

```text
Width: 1366px
Height: 768px
```

---

## 8.3 Sidebar Design

The sidebar should contain the main navigation links.

### Sidebar Items

```text
Dashboard
Books Management
Student Management
Issue Book
Return Book
Reports
Settings
```

### Sidebar Behavior

- Highlight active page.
- Use icons if possible.
- Keep labels clear.
- Keep sidebar fixed.
- Avoid too many items.

### Sidebar Width

```text
220px - 260px
```

---

## 8.4 Top Bar Design

The top bar should display:

- Application name
- School/library name
- Current date
- Optional backup button
- Optional user label: Librarian

Example:

```text
School Library Management System        ABC Public School Library
```

---

## 9. Page Design Structure

Every page should follow this pattern:

```text
Page Header
↓
Short Description
↓
Action Buttons
↓
Search / Filter Area
↓
Main Content
↓
Footer / Status Message
```

Example:

```text
Books Management
Manage all library books, quantities, and availability.

[Add Book] [Import from Excel] [Export to Excel]

Search: [________________] Category: [All v] Status: [Active v]

Books Table
```

---

## 10. Dashboard Design

## 10.1 Dashboard Purpose

The Dashboard gives a quick overview of the library.

---

## 10.2 Dashboard Cards

Use cards to show key statistics.

### Cards

| Card | Description |
|---|---|
| Total Books | Total number of book copies |
| Available Books | Books currently available |
| Issued Books | Books currently issued |
| Total Students | Registered students |
| Pending Returns | Books not returned |
| Overdue Books | Books past due date |
| Low Stock | Books below minimum quantity |

---

## 10.3 Dashboard Layout

```text
Dashboard
Manage and monitor library activity.

+----------------+----------------+----------------+
| Total Books    | Available      | Issued Books   |
| 1,250          | 980            | 270            |
+----------------+----------------+----------------+

+----------------+----------------+----------------+
| Students       | Pending Return | Overdue Books  |
| 650            | 45             | 12             |
+----------------+----------------+----------------+

Recent Issues Table
Recent Returns Table
```

---

## 10.4 Dashboard Card Style

| Property | Value |
|---|---|
| Background | White |
| Border | Light gray |
| Border radius | 10px - 14px |
| Padding | 16px - 24px |
| Title color | Gray |
| Number color | Dark |
| Icon | Optional |
| Shadow | Soft shadow |

---

## 11. Books Management Design

## 11.1 Purpose

The Books Management page is used to add, edit, search, and manage book quantities.

---

## 11.2 Main Actions

Buttons at top:

```text
[Add Book] [Import from Excel] [Export to Excel]
```

---

## 11.3 Book Search and Filters

Search field:

```text
Search by title, author, ISBN, category, or rack number
```

Filters:

- Category
- Status
- Availability
- Low-stock only

---

## 11.4 Books Table Columns

| Column | Description |
|---|---|
| Book ID | Internal book ID |
| Title | Book title |
| Author | Author name |
| Category | Subject/category |
| ISBN | ISBN number |
| Rack No. | Shelf location |
| Total Qty | Total copies |
| Available Qty | Available copies |
| Status | Active/inactive |
| Actions | Edit / Deactivate |

---

## 11.5 Book Availability Badge

Use badges for availability.

| Status | Badge Color |
|---|---|
| Available | Green |
| Low Stock | Orange |
| Not Available | Red |
| Inactive | Gray |

Example:

```text
Available
Low Stock
Not Available
Inactive
```

---

## 11.6 Add/Edit Book Form Design

Form fields:

```text
Book Title *
Author
Category
ISBN
Publisher
Rack Number
Total Quantity *
Status
```

Buttons:

```text
[Save Book] [Cancel]
```

Required fields should show an asterisk `*`.

---

## 12. Student Management Design

## 12.1 Purpose

The Student Management page is used to manage student records.

---

## 12.2 Main Actions

Buttons:

```text
[Add Student] [Import from Excel] [Export to Excel]
```

---

## 12.3 Student Search and Filters

Search field:

```text
Search by student ID, name, class, division, or phone
```

Filters:

- Class
- Division
- Status

---

## 12.4 Students Table Columns

| Column | Description |
|---|---|
| Student ID | Admission number or student code |
| Name | Student name |
| Class | Class |
| Division | Division |
| Phone | Phone number |
| Email | Email address |
| Status | Active/inactive |
| Actions | Edit / View History / Deactivate |

---

## 12.5 Add/Edit Student Form Design

Form fields:

```text
Student ID *
Student Name *
Class
Division
Phone
Email
Address
Status
```

Buttons:

```text
[Save Student] [Cancel]
```

---

## 13. Issue Book Page Design

## 13.1 Purpose

The Issue Book page is used when a student takes a book.

---

## 13.2 Layout

Recommended layout:

```text
Issue Book

+--------------------------+--------------------------+
| Select Student           | Select Book              |
| Search student           | Search book              |
| Student details card     | Book details card        |
+--------------------------+--------------------------+

Issue Date
Due Date
Remarks

[Issue Book]
```

---

## 13.3 Student Selection

The librarian should be able to search by:

- Student ID
- Student name
- Class
- Phone number

After selection, show:

```text
Student Name
Student ID
Class
Division
Pending Books
```

---

## 13.4 Book Selection

The librarian should be able to search by:

- Book title
- Author
- ISBN
- Category
- Rack number

After selection, show:

```text
Book Title
Author
Category
Available Quantity
Rack Number
```

---

## 13.5 Issue Form Fields

| Field | Required |
|---|---|
| Student | Yes |
| Book | Yes |
| Issue Date | Yes |
| Due Date | Yes |
| Remarks | No |

---

## 13.6 Issue Button Behavior

The Issue Book button should be disabled when:

- No student is selected.
- No book is selected.
- Available quantity is 0.
- Selected student is inactive.
- Selected book is inactive.

Show clear warnings before saving.

---

## 14. Return Book Page Design

## 14.1 Purpose

The Return Book page is used to return issued books.

---

## 14.2 Layout

```text
Return Book

Search pending issue:
[Student ID / Student Name / Book Title]

Pending Issue Table

Selected Issue Details

Return Date
Remarks

[Return Book]
```

---

## 14.3 Pending Issue Table Columns

| Column | Description |
|---|---|
| Issue ID | Issue record ID |
| Student ID | Student code |
| Student Name | Student name |
| Book Title | Book title |
| Issue Date | Date issued |
| Due Date | Expected return date |
| Overdue Days | Number of overdue days |
| Status | ISSUED |
| Actions | Return |

---

## 14.4 Overdue Highlighting

Use visual highlights:

| Condition | Style |
|---|---|
| Due today | Orange badge |
| Overdue | Red badge |
| Not overdue | Green or normal badge |

---

## 15. Reports Page Design

## 15.1 Purpose

The Reports page helps the librarian view and export records.

---

## 15.2 Report Types

Reports:

- All books report
- Available books report
- Issued books report
- Returned books report
- Pending returns report
- Overdue books report
- Student report
- Student-wise issue history
- Date-wise issue report
- Date-wise return report
- Low-stock report

---

## 15.3 Reports Layout

```text
Reports

Report Type: [Pending Returns v]
Date From: [date]
Date To: [date]
Class: [All v]
Status: [All v]

[Generate Report] [Export to Excel]

Report Table
```

---

## 15.4 Report Table Design

Use a clean table with:

- Column headers
- Alternating row background
- Search/filter option
- Horizontal scrolling if needed
- Export button

---

## 15.5 Export Button

The Export to Excel button should be visible and consistent.

```text
[Export to Excel]
```

After export:

```text
Report exported successfully.
File saved in exports folder.
```

---

## 16. Settings Page Design

## 16.1 Purpose

The Settings page is used to configure basic app settings.

---

## 16.2 Settings Fields

| Setting | Description |
|---|---|
| School Name | Name of the school |
| Library Name | Name of the library |
| Default Due Days | Default return period |
| Low Stock Limit | Quantity level for low-stock warning |
| Export Folder | Excel report output folder |
| Backup Folder | Backup output folder |
| Theme | Light theme by default |

---

## 16.3 Settings Buttons

```text
[Save Settings]
[Backup Database]
[Export Full Backup to Excel]
[Restore Backup]
```

---

## 17. UI Components

## 17.1 Buttons

### Primary Button

Used for main actions.

Examples:

```text
Add Book
Save Book
Issue Book
Return Book
Generate Report
```

Style:

- Blue background
- White text
- Rounded corners
- Medium padding

---

### Secondary Button

Used for less important actions.

Examples:

```text
Cancel
Clear
Reset Filter
```

Style:

- White background
- Gray border
- Dark text

---

### Danger Button

Used for delete/deactivate actions.

Examples:

```text
Deactivate
Delete
```

Style:

- Red background or red outline
- Warning confirmation before action

---

### Success Button

Used for export/backup actions.

Examples:

```text
Export to Excel
Backup Database
```

Style:

- Green background
- White text

---

## 17.2 Input Fields

Input fields should have:

- Clear labels
- Placeholder text
- Required field indicator
- Error message below field
- Consistent height

Example:

```text
Book Title *
[ Enter book title ]

Book title is required.
```

---

## 17.3 Tables

Tables are used for:

- Books
- Students
- Issue records
- Return records
- Reports

Table design:

- Sticky header if possible
- Clear column names
- Alternating row color
- Action buttons at the end
- Search/filter above table
- Empty state message when no data is available

---

## 17.4 Cards

Cards are used on the Dashboard and detail screens.

Card style:

- White background
- Rounded corners
- Soft border
- Optional icon
- Clear title
- Large number/value

---

## 17.5 Badges

Badges show statuses.

| Status | Badge Color |
|---|---|
| ACTIVE | Green |
| INACTIVE | Gray |
| ISSUED | Blue |
| RETURNED | Green |
| OVERDUE | Red |
| LOW STOCK | Orange |
| NOT AVAILABLE | Red |

---

## 17.6 Dialogs / Popups

Dialogs should be used for:

- Add forms
- Edit forms
- Confirmation messages
- Error alerts
- Export success messages
- Backup restore warning

Example confirmation:

```text
Are you sure you want to deactivate this book?
This action will hide the book from issue list but keep old records.
[Cancel] [Deactivate]
```

---

## 18. Empty State Design

When there is no data, show a helpful message.

### Books Empty State

```text
No books added yet.
Click “Add Book” to add your first library book.
```

### Students Empty State

```text
No students added yet.
Click “Add Student” to register a student.
```

### Pending Returns Empty State

```text
No pending returns.
All issued books are returned.
```

### Reports Empty State

```text
No records found for the selected filters.
Try changing the filter options.
```

---

## 19. Validation Message Design

Validation messages should be simple and clear.

Examples:

| Situation | Message |
|---|---|
| Missing book title | Book title is required |
| Missing quantity | Quantity is required |
| Invalid quantity | Quantity must be a valid number |
| Quantity is 0 | This book is currently not available |
| Duplicate issue | This student already has this book issued |
| Missing student | Please select a student |
| Missing book | Please select a book |
| Invalid date | Due date cannot be earlier than issue date |
| Already returned | This book has already been returned |

---

## 20. Notification Design

Use short notification messages after actions.

### Success Messages

```text
Book added successfully.
Student added successfully.
Book issued successfully.
Book returned successfully.
Report exported successfully.
Backup created successfully.
```

### Error Messages

```text
Unable to save data. Please try again.
This book is not available.
Invalid Excel file format.
Backup failed. Please check folder permission.
```

---

## 21. Accessibility Considerations

The app should be usable by different types of users.

### Accessibility Rules

- Use readable font size.
- Maintain strong color contrast.
- Do not depend only on color for status.
- Use icons plus text where possible.
- Keep buttons large enough to click.
- Support keyboard navigation where possible.
- Show clear focus states.
- Avoid very small table text.
- Use simple language.

### Recommended Minimum Sizes

| Element | Minimum Size |
|---|---|
| Button height | 36px |
| Input height | 36px |
| Table row height | 34px |
| Body font | 13px |
| Page title | 22px |

---

## 22. Responsive / Resizable Desktop Behavior

Even though this is a desktop application, the window should handle resizing.

### Behavior

- Sidebar remains fixed.
- Main content should scroll vertically.
- Tables should support horizontal scroll if needed.
- Forms should not overflow.
- Buttons should wrap or stay aligned.
- Dashboard cards should move to the next row if width is small.

### Minimum Window Size

```text
1100px × 700px
```

---

## 23. Excel Import/Export UI Design

## 23.1 Import from Excel

Import button location:

- Books Management page
- Student Management page

Import flow:

```text
Click Import from Excel
↓
Choose Excel file
↓
Preview data
↓
Show valid and invalid rows
↓
Click Import
↓
Save valid rows to SQLite
```

### Import Result Message

```text
Import completed.
Valid rows imported: 120
Skipped rows: 5
```

---

## 23.2 Export to Excel

Export button location:

- Books Management page
- Student Management page
- Reports page
- Settings backup section

Export flow:

```text
Click Export to Excel
↓
Select save location or use default exports folder
↓
Generate Excel file
↓
Show success message
```

---

## 24. Backup and Restore UI Design

## 24.1 Backup Section

Location:

```text
Settings → Backup
```

Buttons:

```text
[Backup Database]
[Export Full Backup to Excel]
```

Show last backup date:

```text
Last Backup: 06 July 2026, 10:30 AM
```

---

## 24.2 Restore Section

Button:

```text
[Restore Backup]
```

Warning message:

```text
Restoring backup will replace the current data.
Please create a backup before continuing.
```

Buttons:

```text
[Cancel] [Continue Restore]
```

---

## 25. Security Design

For version 1, login can be optional.

If login is added, use:

```text
Login Screen
↓
Dashboard
```

### Login Screen Fields

```text
Username
Password
[Login]
```

### Login Design Rules

- Simple login form
- Show school/library name
- Hide password input
- Show clear error for invalid login
- Remember last username only if needed

---

## 26. Recommended Icons

Icons are optional but can improve usability.

Suggested icons:

| Menu | Icon Idea |
|---|---|
| Dashboard | Home / Chart |
| Books | Book |
| Students | Users |
| Issue Book | Arrow Out / Book Open |
| Return Book | Arrow In / Return |
| Reports | File / Chart |
| Settings | Gear |
| Excel Export | Spreadsheet |
| Backup | Database / Save |

Use icons only if they keep the UI clean.

---

## 27. Screen-by-Screen Summary

## 27.1 Dashboard

Purpose:

```text
Show complete library summary.
```

Main UI:

- Statistics cards
- Recent issued books
- Recent returns
- Quick action buttons

---

## 27.2 Books Management

Purpose:

```text
Manage books and quantity.
```

Main UI:

- Search
- Filters
- Books table
- Add/edit form
- Excel import/export

---

## 27.3 Student Management

Purpose:

```text
Manage student records.
```

Main UI:

- Search
- Filters
- Student table
- Add/edit form
- Student issue history

---

## 27.4 Issue Book

Purpose:

```text
Record when a student takes a book.
```

Main UI:

- Student search
- Book search
- Issue date
- Due date
- Issue button

---

## 27.5 Return Book

Purpose:

```text
Record when a student returns a book.
```

Main UI:

- Pending issue search
- Pending issue table
- Return date
- Return button

---

## 27.6 Reports

Purpose:

```text
View and export library reports.
```

Main UI:

- Report type selector
- Filters
- Report table
- Export to Excel button

---

## 27.7 Settings

Purpose:

```text
Manage school, backup, and app settings.
```

Main UI:

- School name
- Due days
- Low-stock limit
- Backup options
- Export folder

---

## 28. Suggested UI Wireframe

```text
+--------------------------------------------------------------------------------+
| School Library Management System                         ABC Public School      |
+-------------------------+------------------------------------------------------+
| Dashboard               | Dashboard                                            |
| Books Management        | Manage and monitor library activity                  |
| Student Management      |                                                      |
| Issue Book              | +------------+ +------------+ +------------+          |
| Return Book             | | Total Books| | Available  | | Issued     |          |
| Reports                 | | 1250       | | 980        | | 270        |          |
| Settings                | +------------+ +------------+ +------------+          |
|                         |                                                      |
|                         | Recent Issues                                        |
|                         | ---------------------------------------------------- |
|                         | Student | Book | Issue Date | Due Date | Status      |
+-------------------------+------------------------------------------------------+
```

---

## 29. UI Text Guidelines

Use simple words.

Good examples:

```text
Add Book
Return Book
Pending Returns
Export to Excel
Book added successfully
This book is not available
```

Avoid technical words:

```text
Insert record
Execute query
Foreign key error
Database transaction failed
```

Instead, show user-friendly messages.

---

## 30. Final Design Recommendation

The final design should be a clean desktop admin-style application with:

- Left sidebar navigation
- Dashboard-first layout
- White card-based interface
- Simple forms
- Searchable tables
- Clear action buttons
- Status badges
- Excel import/export buttons
- Backup controls in settings
- Safe validation messages

### Final Recommended Design Stack

```text
UI Framework: PySide6
Theme: Light professional school-office style
Layout: Sidebar + main content
Database: SQLite
Excel: openpyxl import/export
Packaging: PyInstaller
```

### Final Design Summary

The School Library Management System should feel like a professional but simple office application. The librarian should immediately understand where to add books, where to add students, how to issue books, how to return books, and how to export reports. The design must prioritize clarity, speed, and data safety over visual complexity.
